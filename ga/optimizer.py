"""
GA最適化メインクラス
"""
import random
from typing import List, Optional, Dict, Tuple, Callable
from dataclasses import dataclass
from datetime import date
from deap import base, creator, tools, algorithms
from database.base import SessionLocal
from database.models.staff import Staff
from database.models.hospital import Hospital
from database.models.assignment import Assignment
from repositories.staff_repository import StaffRepository
from repositories.hospital_repository import HospitalRepository
from repositories.assignment_repository import AssignmentRepository
from repositories.hospital_choice_repository import HospitalChoiceRepository
from services.config_service import config_service
from config.constants import StaffType, MismatchReason
from ga.fitness import FitnessContext, load_fitness_context, calculate_fitness
from ga.operators import (
    crossover_two_point,
    mutate_random,
    mutate_capacity_aware,
    mutate_hope_aware,
    select_tournament
)
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class OptimizationResult:
    """最適化結果"""
    # 最良個体
    best_individual: List[int]
    # 最良適合度
    best_fitness: float
    # 世代数
    generations: int
    # 割り当て結果 [(resident_id, hospital_id, hope_rank, fitness_score), ...]
    assignments: List[Tuple[int, int, int, float]]
    # 統計情報
    stats: Dict


class GAOptimizer:
    """
    遺伝的アルゴリズムによる専攻医配置最適化

    DEAPライブラリを使用
    """

    def __init__(self, fiscal_year: Optional[int] = None):
        """
        Args:
            fiscal_year: 対象年度（省略時は設定から取得）
        """
        self.fiscal_year = fiscal_year or int(
            config_service.get(config_service.Keys.FISCAL_YEAR, "2025")
        )

        # GA設定を読み込み
        self.population_size = int(
            config_service.get(config_service.Keys.GA_POPULATION_SIZE, "100")
        )
        self.generations = int(
            config_service.get(config_service.Keys.GA_GENERATIONS, "200")
        )
        self.crossover_prob = float(
            config_service.get(config_service.Keys.GA_CROSSOVER_PROB, "0.7")
        )
        self.mutation_prob = float(
            config_service.get(config_service.Keys.GA_MUTATION_PROB, "0.2")
        )

        # データ
        self.residents: List[Staff] = []
        self.hospitals: List[Hospital] = []
        self.context: Optional[FitnessContext] = None

        # DEAP設定
        self._setup_deap()

        logger.info(f"GAOptimizer initialized for fiscal year {self.fiscal_year}")

    def _setup_deap(self):
        """DEAPの設定"""
        # 既存のクラスがあれば削除
        if hasattr(creator, "FitnessMax"):
            del creator.FitnessMax
        if hasattr(creator, "Individual"):
            del creator.Individual

        # 適合度クラス（最大化）
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))

        # 個体クラス
        creator.create("Individual", list, fitness=creator.FitnessMax)

        # ツールボックス
        self.toolbox = base.Toolbox()

    def load_data(self) -> bool:
        """
        データを読み込み

        Returns:
            bool: 成功時True
        """
        try:
            with SessionLocal() as db:
                # 専攻医を取得
                staff_repo = StaffRepository(db)
                self.residents = staff_repo.get_by_staff_type(StaffType.RESIDENT_DOCTOR)

                # 病院を取得
                hospital_repo = HospitalRepository(db)
                self.hospitals = hospital_repo.get_all()

            if not self.residents:
                logger.warning("No residents found")
                return False

            if not self.hospitals:
                logger.warning("No hospitals found")
                return False

            # コンテキストを読み込み
            self.context = load_fitness_context(
                self.fiscal_year, self.residents, self.hospitals
            )

            # DEAP演算子を登録
            self._register_operators()

            logger.info(f"Loaded {len(self.residents)} residents, {len(self.hospitals)} hospitals")
            return True

        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return False

    def _register_operators(self):
        """DEAP演算子を登録"""
        num_hospitals = len(self.hospitals)

        # 遺伝子生成（ランダムな病院インデックス）
        self.toolbox.register("attr_hospital", random.randint, 0, num_hospitals - 1)

        # 個体生成
        self.toolbox.register(
            "individual",
            tools.initRepeat,
            creator.Individual,
            self.toolbox.attr_hospital,
            n=len(self.residents)
        )

        # 集団生成
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        # 評価関数
        self.toolbox.register("evaluate", self._evaluate)

        # 選択（トーナメント）
        self.toolbox.register("select", tools.selTournament, tournsize=3)

        # 交叉
        self.toolbox.register("mate", crossover_two_point)

        # 突然変異（複合）
        self.toolbox.register("mutate", self._mutate)

    def _evaluate(self, individual: List[int]) -> Tuple[float,]:
        """評価関数"""
        return calculate_fitness(individual, self.context)

    def _mutate(self, individual: List[int]) -> Tuple[List[int],]:
        """複合突然変異"""
        # ランダム突然変異
        individual, = mutate_random(individual, len(self.hospitals), indpb=0.05)

        # 定員考慮突然変異
        individual, = mutate_capacity_aware(individual, self.context, indpb=0.3)

        # 希望考慮突然変異
        individual, = mutate_hope_aware(individual, self.context, indpb=0.2)

        return (individual,)

    def optimize(
        self,
        progress_callback: Optional[Callable[[int, float], None]] = None
    ) -> OptimizationResult:
        """
        最適化を実行

        Args:
            progress_callback: 進捗コールバック (世代, 適合度) -> None

        Returns:
            OptimizationResult: 最適化結果
        """
        if not self.context:
            raise ValueError("Data not loaded. Call load_data() first.")

        logger.info(f"Starting GA optimization: pop={self.population_size}, gen={self.generations}")

        # 初期集団を生成
        population = self.toolbox.population(n=self.population_size)

        # 統計
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", lambda x: sum(v[0] for v in x) / len(x) if x else 0)
        stats.register("max", lambda x: max(v[0] for v in x) if x else 0)
        stats.register("min", lambda x: min(v[0] for v in x) if x else 0)

        # 殿堂入り（最良個体を保存）
        hof = tools.HallOfFame(1)

        # 進化ループ
        logbook = tools.Logbook()

        # 初期評価
        fitnesses = map(self.toolbox.evaluate, population)
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

        hof.update(population)
        record = stats.compile(population)
        logbook.record(gen=0, **record)

        if progress_callback:
            progress_callback(0, record["max"])

        # 世代ループ
        for gen in range(1, self.generations + 1):
            # 選択
            offspring = self.toolbox.select(population, len(population))
            offspring = list(map(self.toolbox.clone, offspring))

            # 交叉
            for i in range(0, len(offspring) - 1, 2):
                if random.random() < self.crossover_prob:
                    offspring[i][:], offspring[i + 1][:] = self.toolbox.mate(
                        offspring[i], offspring[i + 1]
                    )
                    del offspring[i].fitness.values
                    del offspring[i + 1].fitness.values

            # 突然変異
            for mutant in offspring:
                if random.random() < self.mutation_prob:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            # 再評価
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # 集団を更新
            population[:] = offspring

            # 統計更新
            hof.update(population)
            record = stats.compile(population)
            logbook.record(gen=gen, **record)

            if progress_callback and gen % 10 == 0:
                progress_callback(gen, record["max"])

            # 早期終了チェック（収束判定）
            if gen > 50 and abs(record["max"] - record["avg"]) < 0.001:
                logger.info(f"Converged at generation {gen}")
                break

        # 最良個体
        best = hof[0]
        best_fitness = best.fitness.values[0]

        # 割り当て結果を生成
        assignments = self._generate_assignments(best)

        logger.info(f"Optimization complete. Best fitness: {best_fitness:.4f}")

        return OptimizationResult(
            best_individual=list(best),
            best_fitness=best_fitness,
            generations=gen,
            assignments=assignments,
            stats={"logbook": logbook}
        )

    def _generate_assignments(
        self, individual: List[int]
    ) -> List[Tuple[int, int, int, float]]:
        """
        割り当て結果を生成

        Args:
            individual: 最良個体

        Returns:
            List[Tuple[int, int, int, float]]: (resident_id, hospital_id, hope_rank, fitness)
        """
        assignments = []

        for i, resident in enumerate(self.residents):
            hospital_idx = individual[i]
            hospital = self.hospitals[hospital_idx]

            # 希望順位を取得
            choices = self.context.hospital_choices.get(resident.id, {})
            hope_rank = 0
            for rank, h_id in choices.items():
                if h_id == hospital.id:
                    hope_rank = rank
                    break

            # 個別の適合度を計算
            individual_fitness = calculate_fitness([hospital_idx], FitnessContext(
                residents=[resident],
                hospitals=self.hospitals,
                hospital_id_to_idx=self.context.hospital_id_to_idx,
                resident_id_to_idx={resident.id: 0},
                fiscal_year=self.fiscal_year,
                hospital_choices={resident.id: choices},
                staff_weights={resident.id: self.context.staff_weights.get(resident.id, {})},
                admin_evaluations={resident.id: self.context.admin_evaluations.get(resident.id, {})},
                commute_cache=self.context.commute_cache,
                staff_factors=self.context.staff_factors,
                admin_factors=self.context.admin_factors,
                hospital_capacities=self.context.hospital_capacities
            ))[0]

            assignments.append((resident.id, hospital.id, hope_rank, individual_fitness))

        return assignments

    def save_assignments(self, result: OptimizationResult) -> int:
        """
        割り当て結果をデータベースに保存

        Args:
            result: 最適化結果

        Returns:
            int: 保存した件数
        """
        saved_count = 0

        with SessionLocal() as db:
            repo = AssignmentRepository(db)
            choice_repo = HospitalChoiceRepository(db)

            # 既存の割り当てを削除
            existing = repo.get_by_fiscal_year(self.fiscal_year)
            for assignment in existing:
                repo.delete(assignment.id)

            # 新しい割り当てを保存
            for resident_id, hospital_id, hope_rank, fitness in result.assignments:
                # 通勤時間を取得
                commute_time = self.context.commute_cache.get(
                    (resident_id, hospital_id), None
                )

                # アンマッチ判定
                is_mismatch = hope_rank == 0
                mismatch_reason = MismatchReason.NO_PREFERENCE if is_mismatch else None

                # 開始日・終了日（年度の4月1日〜翌年3月31日）
                start_date = date(self.fiscal_year, 4, 1)
                end_date = date(self.fiscal_year + 1, 3, 31)

                assignment_data = {
                    "staff_id": resident_id,
                    "hospital_id": hospital_id,
                    "fiscal_year": self.fiscal_year,
                    "start_date": start_date,
                    "end_date": end_date,
                    "mismatch_flag": is_mismatch,
                    "mismatch_reason": mismatch_reason,
                    "fitness_score": fitness,
                    "hope_rank": hope_rank if hope_rank > 0 else None,
                    "commute_time": int(commute_time) if commute_time else None
                }

                repo.create(assignment_data)
                saved_count += 1

            logger.info(f"Saved {saved_count} assignments")

        return saved_count


def run_optimization(
    fiscal_year: Optional[int] = None,
    progress_callback: Optional[Callable[[int, float], None]] = None,
    save_results: bool = True
) -> OptimizationResult:
    """
    最適化を実行するヘルパー関数

    Args:
        fiscal_year: 年度
        progress_callback: 進捗コールバック
        save_results: 結果をDBに保存するか

    Returns:
        OptimizationResult: 最適化結果
    """
    optimizer = GAOptimizer(fiscal_year)

    if not optimizer.load_data():
        raise ValueError("Failed to load data for optimization")

    result = optimizer.optimize(progress_callback)

    if save_results:
        optimizer.save_assignments(result)

    return result

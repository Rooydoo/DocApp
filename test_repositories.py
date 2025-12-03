"""
リポジトリテストスクリプト
基本的なCRUD操作をテスト
"""
from database.connection import get_db_session
from repositories import HospitalRepository, StaffRepository
from config.constants import StaffType
from utils.logger import get_logger

logger = get_logger(__name__)


def test_hospital_repository():
    """病院リポジトリのテスト"""
    print("\n" + "=" * 60)
    print("Testing Hospital Repository")
    print("=" * 60)
    
    with get_db_session() as db:
        repo = HospitalRepository(db)
        
        # Create
        hospital_data = {
            "name": "テスト病院",
            "director_name": "田中太郎",
            "address": "東京都千代田区霞が関1-1-1",
            "capacity": 5,
            "rotation_months": 6,
            "annual_salary": 6000000.00,
            "outpatient_flag": True,
            "notes": "テスト用病院"
        }
        
        hospital = repo.create(hospital_data)
        print(f"✓ Created: {hospital}")
        
        # Read
        retrieved = repo.get(hospital.id)
        print(f"✓ Retrieved: {retrieved}")
        
        # Update
        updated = repo.update(hospital.id, {"capacity": 10})
        print(f"✓ Updated capacity: {updated.capacity}")
        
        # Search
        found = repo.get_by_name("テスト病院")
        print(f"✓ Found by name: {found}")
        
        # Count
        count = repo.count()
        print(f"✓ Total hospitals: {count}")
        
        # Delete
        repo.delete(hospital.id)
        print(f"✓ Deleted hospital id={hospital.id}")


def test_staff_repository():
    """職員リポジトリのテスト"""
    print("\n" + "=" * 60)
    print("Testing Staff Repository")
    print("=" * 60)
    
    with get_db_session() as db:
        repo = StaffRepository(db)
        
        # Create
        staff_data = {
            "name": "山田花子",
            "email": "yamada@example.com",
            "phone": "09012345678",
            "staff_type": StaffType.RESIDENT_DOCTOR,
            "address": "東京都港区六本木1-1-1",
            "rotation_months": 12,
            "notes": "テスト用職員"
        }
        
        staff = repo.create(staff_data)
        print(f"✓ Created: {staff}")
        
        # Read
        retrieved = repo.get(staff.id)
        print(f"✓ Retrieved: {retrieved}")
        
        # Get by email
        found = repo.get_by_email("yamada@example.com")
        print(f"✓ Found by email: {found}")
        
        # Get resident doctors
        resident_doctors = repo.get_resident_doctors()
        print(f"✓ Resident doctors count: {len(resident_doctors)}")
        
        # Update
        updated = repo.update(staff.id, {"phone": "08011112222"})
        print(f"✓ Updated phone: {updated.phone}")
        
        # Count by type
        count = repo.count_by_staff_type(StaffType.RESIDENT_DOCTOR)
        print(f"✓ Resident doctors: {count}")
        
        # Delete
        repo.delete(staff.id)
        print(f"✓ Deleted staff id={staff.id}")


def main():
    print("=" * 60)
    print("Repository CRUD Tests")
    print("=" * 60)
    
    try:
        test_hospital_repository()
        test_staff_repository()
        
        print("\n" + "=" * 60)
        print("All repository tests passed!")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n✗ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()

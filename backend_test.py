import requests
import sys
import json
from datetime import datetime

class CommissionSystemTester:
    def __init__(self, base_url="https://deliver-track-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tokens = {}  # Store tokens for different users
        self.users = {}   # Store user data
        self.tests_run = 0
        self.tests_passed = 0
        
        # Commission rates for validation
        self.commission_rates = {
            "BKO": 3.50, "PYW": 3.50, "NYC": 3.50,
            "GKY": 7.50, "GSD": 7.50, "AUA": 10.00
        }
        self.truck_types = ["BKO", "PYW", "NYC", "GKY", "GSD", "AUA"]

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_user_registration(self):
        """Test user registration for different roles"""
        print("\n=== TESTING USER REGISTRATION ===")
        
        # Test driver registration
        timestamp = datetime.now().strftime('%H%M%S')
        driver_data = {
            "username": f"test_driver_{timestamp}",
            "password": "TestPass123!",
            "role": "driver"
        }
        
        success, response = self.run_test(
            "Driver Registration",
            "POST",
            "auth/register",
            200,
            data=driver_data
        )
        
        if success and 'token' in response:
            self.tokens['driver'] = response['token']
            self.users['driver'] = response['user']
            print(f"Driver registered: {response['user']['username']}")
        
        # Test helper registration
        helper_data = {
            "username": f"test_helper_{timestamp}",
            "password": "TestPass123!",
            "role": "helper"
        }
        
        success, response = self.run_test(
            "Helper Registration",
            "POST",
            "auth/register",
            200,
            data=helper_data
        )
        
        if success and 'token' in response:
            self.tokens['helper'] = response['token']
            self.users['helper'] = response['user']
            print(f"Helper registered: {response['user']['username']}")
        
        # Test admin registration
        admin_data = {
            "username": f"test_admin_{timestamp}",
            "password": "TestPass123!",
            "role": "admin"
        }
        
        success, response = self.run_test(
            "Admin Registration",
            "POST",
            "auth/register",
            200,
            data=admin_data
        )
        
        if success and 'token' in response:
            self.tokens['admin'] = response['token']
            self.users['admin'] = response['user']
            print(f"Admin registered: {response['user']['username']}")
        
        # Test duplicate username
        self.run_test(
            "Duplicate Username Registration",
            "POST",
            "auth/register",
            400,
            data=driver_data
        )
        
        # Test invalid role
        invalid_role_data = {
            "username": f"test_invalid_{timestamp}",
            "password": "TestPass123!",
            "role": "invalid_role"
        }
        
        self.run_test(
            "Invalid Role Registration",
            "POST",
            "auth/register",
            400,
            data=invalid_role_data
        )

    def test_user_login(self):
        """Test user login functionality"""
        print("\n=== TESTING USER LOGIN ===")
        
        if not self.users.get('driver'):
            print("❌ No driver user available for login test")
            return
        
        # Test valid login
        login_data = {
            "username": self.users['driver']['username'],
            "password": "TestPass123!"
        }
        
        success, response = self.run_test(
            "Valid Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'token' in response:
            print(f"Login successful for: {response['user']['username']}")
        
        # Test invalid credentials
        invalid_login = {
            "username": self.users['driver']['username'],
            "password": "WrongPassword"
        }
        
        self.run_test(
            "Invalid Password Login",
            "POST",
            "auth/login",
            401,
            data=invalid_login
        )
        
        # Test non-existent user
        nonexistent_login = {
            "username": "nonexistent_user",
            "password": "TestPass123!"
        }
        
        self.run_test(
            "Non-existent User Login",
            "POST",
            "auth/login",
            401,
            data=nonexistent_login
        )

    def test_auth_me_endpoint(self):
        """Test the /auth/me endpoint"""
        print("\n=== TESTING AUTH ME ENDPOINT ===")
        
        if not self.tokens.get('driver'):
            print("❌ No driver token available for auth/me test")
            return
        
        # Test with valid token
        headers = {'Authorization': f'Bearer {self.tokens["driver"]}'}
        success, response = self.run_test(
            "Get Current User Info",
            "GET",
            "auth/me",
            200,
            headers=headers
        )
        
        if success:
            print(f"Current user: {response.get('username')} ({response.get('role')})")
        
        # Test with invalid token
        invalid_headers = {'Authorization': 'Bearer invalid_token'}
        self.run_test(
            "Invalid Token Auth",
            "GET",
            "auth/me",
            401,
            headers=invalid_headers
        )

    def test_user_deliveries(self):
        """Test user delivery endpoints"""
        print("\n=== TESTING USER DELIVERIES ===")
        
        if not self.tokens.get('driver'):
            print("❌ No driver token available for delivery test")
            return
        
        # Test get my deliveries
        headers = {'Authorization': f'Bearer {self.tokens["driver"]}'}
        success, response = self.run_test(
            "Get My Deliveries",
            "GET",
            "deliveries/my",
            200,
            headers=headers
        )
        
        if success:
            stats = response.get('stats', {})
            print(f"Total deliveries: {stats.get('total_deliveries', 0)}")
            print(f"Total commission: R$ {stats.get('total_commission', 0)}")
            
            # Validate commission rates
            commission_rates = response.get('commission_rates', {})
            for truck, rate in self.commission_rates.items():
                if commission_rates.get(truck) != rate:
                    print(f"❌ Commission rate mismatch for {truck}: expected {rate}, got {commission_rates.get(truck)}")
                else:
                    print(f"✅ Commission rate correct for {truck}: {rate}")

    def test_admin_functionality(self):
        """Test admin-only functionality"""
        print("\n=== TESTING ADMIN FUNCTIONALITY ===")
        
        if not self.tokens.get('admin'):
            print("❌ No admin token available for admin tests")
            return
        
        if not self.users.get('driver'):
            print("❌ No driver user available for admin tests")
            return
        
        admin_headers = {'Authorization': f'Bearer {self.tokens["admin"]}'}
        driver_headers = {'Authorization': f'Bearer {self.tokens["driver"]}'}
        
        # Test get all users (admin only)
        success, response = self.run_test(
            "Get All Users (Admin)",
            "GET",
            "deliveries/all-users",
            200,
            headers=admin_headers
        )
        
        if success:
            users = response.get('users', [])
            print(f"Found {len(users)} users")
            for user in users:
                print(f"  - {user['username']} ({user['role']}): {user['total_deliveries']} deliveries, R$ {user['total_commission']}")
        
        # Test non-admin access to admin endpoint
        self.run_test(
            "Get All Users (Non-Admin)",
            "GET",
            "deliveries/all-users",
            403,
            headers=driver_headers
        )
        
        # Test update deliveries (admin only)
        update_data = {
            "userId": self.users['driver']['id'],
            "truck_type": "BKO",
            "count": 5
        }
        
        success, response = self.run_test(
            "Update Deliveries (Admin)",
            "POST",
            "deliveries/update",
            200,
            data=update_data,
            headers=admin_headers
        )
        
        if success:
            stats = response.get('stats', {})
            expected_commission = 5 * self.commission_rates['BKO']
            actual_commission = stats.get('total_commission', 0)
            if abs(actual_commission - expected_commission) < 0.01:
                print(f"✅ Commission calculation correct: R$ {actual_commission}")
            else:
                print(f"❌ Commission calculation incorrect: expected R$ {expected_commission}, got R$ {actual_commission}")
        
        # Test non-admin update deliveries
        self.run_test(
            "Update Deliveries (Non-Admin)",
            "POST",
            "deliveries/update",
            403,
            data=update_data,
            headers=driver_headers
        )
        
        # Test update with invalid truck type
        invalid_update = {
            "userId": self.users['driver']['id'],
            "truck_type": "INVALID",
            "count": 3
        }
        
        self.run_test(
            "Update Invalid Truck Type",
            "POST",
            "deliveries/update",
            400,
            data=invalid_update,
            headers=admin_headers
        )
        
        # Test update for non-existent user
        nonexistent_update = {
            "userId": "nonexistent-user-id",
            "truck_type": "BKO",
            "count": 2
        }
        
        self.run_test(
            "Update Non-existent User",
            "POST",
            "deliveries/update",
            404,
            data=nonexistent_update,
            headers=admin_headers
        )

    def test_monthly_reset(self):
        """Test monthly reset functionality"""
        print("\n=== TESTING MONTHLY RESET ===")
        
        if not self.tokens.get('admin'):
            print("❌ No admin token available for reset test")
            return
        
        admin_headers = {'Authorization': f'Bearer {self.tokens["admin"]}'}
        driver_headers = {'Authorization': f'Bearer {self.tokens["driver"]}'}
        
        # Test admin reset
        success, response = self.run_test(
            "Monthly Reset (Admin)",
            "POST",
            "deliveries/reset-month",
            200,
            data={},
            headers=admin_headers
        )
        
        if success:
            updated_count = response.get('updated_count', 0)
            print(f"Reset {updated_count} delivery records")
        
        # Test non-admin reset
        self.run_test(
            "Monthly Reset (Non-Admin)",
            "POST",
            "deliveries/reset-month",
            403,
            data={},
            headers=driver_headers
        )

    def test_commission_calculation(self):
        """Test commission calculation for all truck types"""
        print("\n=== TESTING COMMISSION CALCULATION ===")
        
        if not self.tokens.get('admin') or not self.users.get('helper'):
            print("❌ Missing admin token or helper user for commission test")
            return
        
        admin_headers = {'Authorization': f'Bearer {self.tokens["admin"]}'}
        helper_headers = {'Authorization': f'Bearer {self.tokens["helper"]}'}
        
        # Test each truck type
        for truck_type in self.truck_types:
            test_count = 3
            update_data = {
                "userId": self.users['helper']['id'],
                "truck_type": truck_type,
                "count": test_count
            }
            
            success, response = self.run_test(
                f"Update {truck_type} Deliveries",
                "POST",
                "deliveries/update",
                200,
                data=update_data,
                headers=admin_headers
            )
            
            if success:
                expected_commission = test_count * self.commission_rates[truck_type]
                # Get updated stats
                success2, delivery_response = self.run_test(
                    f"Get {truck_type} Stats",
                    "GET",
                    "deliveries/my",
                    200,
                    headers=helper_headers
                )
                
                if success2:
                    stats = delivery_response.get('stats', {})
                    deliveries_by_truck = stats.get('deliveries_by_truck', {})
                    actual_count = deliveries_by_truck.get(truck_type, 0)
                    
                    if actual_count == test_count:
                        print(f"✅ {truck_type} delivery count correct: {actual_count}")
                    else:
                        print(f"❌ {truck_type} delivery count incorrect: expected {test_count}, got {actual_count}")

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Commission System API Tests")
        print(f"Testing against: {self.base_url}")
        
        try:
            self.test_user_registration()
            self.test_user_login()
            self.test_auth_me_endpoint()
            self.test_user_deliveries()
            self.test_admin_functionality()
            self.test_commission_calculation()
            self.test_monthly_reset()
            
        except Exception as e:
            print(f"❌ Test suite failed with error: {str(e)}")
        
        # Print final results
        print(f"\n📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    tester = CommissionSystemTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
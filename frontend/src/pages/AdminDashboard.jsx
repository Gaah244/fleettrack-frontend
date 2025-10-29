import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { LogOut, TruckIcon, RefreshCw, Users } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TRUCK_TYPES = ["BKO", "PYW", "NYC", "GKY", "GSD", "AUA"];

const AdminDashboard = ({ user, onLogout }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState(null);
  const [deliveryUpdates, setDeliveryUpdates] = useState({});
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/deliveries/all-users`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUsers(response.data.users);
    } catch (error) {
      toast.error("Failed to fetch users data");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateDelivery = async (userId, truckType) => {
    const count = deliveryUpdates[`${userId}-${truckType}`] || 0;
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API}/deliveries/update`,
        { userId, truck_type: truckType, count: parseInt(count) },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success(`Updated ${truckType} deliveries`);
      fetchUsers();
    } catch (error) {
      toast.error("Failed to update delivery");
    }
  };

  const handleResetMonth = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API}/deliveries/reset-month`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success("All deliveries reset for the new month");
      fetchUsers();
    } catch (error) {
      toast.error("Failed to reset month");
    }
  };

  const openUpdateDialog = (userToUpdate) => {
    setSelectedUser(userToUpdate);
    // Initialize delivery updates with current values
    const updates = {};
    TRUCK_TYPES.forEach(truck => {
      updates[`${userToUpdate.id}-${truck}`] = userToUpdate.deliveries_by_truck[truck] || 0;
    });
    setDeliveryUpdates(updates);
    setDialogOpen(true);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-xl font-semibold text-indigo-600">Loading admin panel...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-indigo-600 rounded-xl">
                <TruckIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-indigo-900">FleetTrack Admin</h1>
                <p className="text-sm text-gray-600">Welcome, {user.username}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button 
                    variant="outline" 
                    className="flex items-center gap-2 text-red-600 border-red-300 hover:bg-red-50"
                    data-testid="reset-month-button"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Reset Month
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Reset Month Deliveries?</AlertDialogTitle>
                    <AlertDialogDescription>
                      This will reset all delivery counts to 0 for all users. This action cannot be undone.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel data-testid="reset-cancel-button">Cancel</AlertDialogCancel>
                    <AlertDialogAction 
                      onClick={handleResetMonth}
                      className="bg-red-600 hover:bg-red-700"
                      data-testid="reset-confirm-button"
                    >
                      Reset
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
              
              <Button 
                onClick={onLogout} 
                variant="outline" 
                className="flex items-center gap-2"
                data-testid="admin-logout-button"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Admin Panel</h2>
          <p className="text-gray-600">Manage all drivers and helpers</p>
        </div>

        {/* Users List */}
        <div className="grid grid-cols-1 gap-6">
          {users.length === 0 ? (
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
              <CardContent className="py-12 text-center">
                <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No users found</p>
              </CardContent>
            </Card>
          ) : (
            users.map((userData) => (
              <Card key={userData.id} className="bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-shadow" data-testid={`user-card-${userData.username}`}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-xl font-bold text-gray-900">{userData.username}</CardTitle>
                      <p className="text-sm text-gray-600 mt-1">
                        <span className="inline-block px-2 py-1 rounded-full bg-indigo-100 text-indigo-700 text-xs font-medium">
                          {userData.role}
                        </span>
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-600">Total Commission</p>
                      <p className="text-2xl font-bold text-indigo-600" data-testid={`user-${userData.username}-commission`}>
                        R$ {userData.total_commission?.toFixed(2) || "0.00"}
                      </p>
                      <p className="text-sm text-gray-500 mt-1" data-testid={`user-${userData.username}-deliveries`}>
                        {userData.total_deliveries} deliveries
                      </p>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-4">
                    {TRUCK_TYPES.map((truck) => (
                      <div key={truck} className="p-3 rounded-lg bg-gray-50 border border-gray-200">
                        <p className="text-xs text-gray-600 font-medium">{truck}</p>
                        <p className="text-lg font-bold text-gray-900" data-testid={`user-${userData.username}-truck-${truck}`}>
                          {userData.deliveries_by_truck[truck] || 0}
                        </p>
                      </div>
                    ))}
                  </div>
                  <Button 
                    onClick={() => openUpdateDialog(userData)} 
                    className="w-full bg-indigo-600 hover:bg-indigo-700"
                    data-testid={`update-deliveries-button-${userData.username}`}
                  >
                    Update Deliveries
                  </Button>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;
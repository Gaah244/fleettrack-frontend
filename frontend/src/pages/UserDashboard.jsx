import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { LogOut, TruckIcon, DollarSign, Package } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UserDashboard = ({ user, onLogout }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/deliveries/my`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data.stats);
    } catch (error) {
      toast.error("Failed to fetch data");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-xl font-semibold text-indigo-600">Loading your dashboard...</div>
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
                <h1 className="text-2xl font-bold text-indigo-900">FleetTrack</h1>
                <p className="text-sm text-gray-600">Welcome, {user.username}</p>
              </div>
            </div>
            <Button 
              onClick={onLogout} 
              variant="outline" 
              className="flex items-center gap-2"
              data-testid="logout-button"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Your Dashboard</h2>
          <p className="text-gray-600">Track your deliveries and commission</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-shadow" data-testid="total-deliveries-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Total Deliveries</CardTitle>
              <Package className="h-5 w-5 text-indigo-600" />
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-gray-900" data-testid="total-deliveries-count">
                {stats?.total_deliveries || 0}
              </div>
              <p className="text-xs text-gray-500 mt-2">Across all truck types</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-indigo-500 to-purple-600 text-white border-0 shadow-lg hover:shadow-xl transition-shadow" data-testid="total-commission-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-indigo-100">Total Commission</CardTitle>
              <DollarSign className="h-5 w-5 text-white" />
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold" data-testid="total-commission-amount">
                R$ {stats?.total_commission?.toFixed(2) || "0.00"}
              </div>
              <p className="text-xs text-indigo-100 mt-2">Current month earnings</p>
            </CardContent>
          </Card>
        </div>

        {/* Deliveries by Truck Type */}
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
          <CardHeader>
            <CardTitle className="text-xl font-bold">Deliveries by Truck Type</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {stats?.deliveries_by_truck && Object.entries(stats.deliveries_by_truck).map(([truck, count]) => {
                const rates = {
                  "BKO": 3.50, "PYW": 3.50, "NYC": 3.50,
                  "GKY": 7.50, "GSD": 7.50, "AUA": 10.00
                };
                const rate = rates[truck];
                const commission = (count * rate).toFixed(2);

                return (
                  <div 
                    key={truck} 
                    className="p-4 rounded-xl border-2 border-gray-200 hover:border-indigo-400 transition-colors bg-white"
                    data-testid={`truck-card-${truck}`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-indigo-600"></div>
                        <h3 className="font-bold text-gray-900">{truck}</h3>
                      </div>
                      <span className="text-xs text-gray-500">R$ {rate}/delivery</span>
                    </div>
                    <div className="mt-3">
                      <p className="text-2xl font-bold text-gray-900" data-testid={`truck-${truck}-count`}>{count}</p>
                      <p className="text-sm text-gray-600 mt-1">deliveries</p>
                      <p className="text-sm font-semibold text-indigo-600 mt-2" data-testid={`truck-${truck}-commission`}>
                        Commission: R$ {commission}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default UserDashboard;
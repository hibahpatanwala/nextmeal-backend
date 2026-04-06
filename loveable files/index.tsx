import { useState } from "react";
import { MapPin } from "lucide-react";
import { FloatingChatbot } from "@/components/FloatingChatbot";
import AuthView from "@/views/AuthView";
import CustomerView from "@/views/CustomerView";
import ChefView from "@/views/ChefView";
import CourierView from "@/views/CourierView";
import ProfilePage from "@/pages/ProfilePage";

export type View = "auth" | "customer" | "chef" | "courier" | "profile";

const Index = () => {
  const [view, setView] = useState<View>("auth");
  const [userId, setUserId] = useState<string | null>(null);
  const [userLocation] = useState("Vile Parle, Mumbai");

  // Mock user data (populated on signup, fallback defaults)
  const [userData, setUserData] = useState({
    name: "",
    email: "",
    phone: "",
    dob: "",
    spiceLevel: 5,
    maxBudget: 1500,
  });

  const handleLogout = () => {
    setView("auth");
    setUserId(null);
    localStorage.removeItem("user_id");
    localStorage.removeItem("user_role");
  };

  const handleLogin = (role: "customer" | "chef" | "courier", id: string) => {
    setUserId(id);
    setView(role);
    localStorage.setItem("user_id", id);
    localStorage.setItem("user_role", role);
  };

  const showGlobalHeader = view !== "auth";

  return (
    <div className="min-h-screen bg-background">
      {/* Global Location Header */}
      {showGlobalHeader && (
        <div className="bg-card/80 backdrop-blur-sm border-b border-border px-4 py-2 flex items-center justify-between sticky top-0 z-50">
          <div className="flex items-center gap-2">
            <MapPin className="w-3.5 h-3.5 text-primary" />
            <div>
              <p className="text-[9px] text-muted-foreground leading-none">Delivering to</p>
              <p className="text-xs font-semibold">{userLocation}</p>
            </div>
          </div>
          {view !== "profile" && (view === "customer" || view === "chef" || view === "courier") && (
            <button
              onClick={() => setView("profile")}
              className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center text-primary text-[10px] font-bold hover:bg-primary/20 transition-colors"
            >
              {(userData.name || "U").charAt(0).toUpperCase()}
            </button>
          )}
        </div>
      )}

      {view === "auth" && <AuthView onLogin={handleLogin} />}
      {view === "customer" && <CustomerView onLogout={handleLogout} userId={userId || "1"} />}
      {view === "chef" && <ChefView onLogout={handleLogout} chefId={userId!} />}
      {view === "courier" && <CourierView onLogout={handleLogout} courierId={userId || "1"} />}
      {view === "profile" && (
        <ProfilePage
          onBack={() => {
            const role = localStorage.getItem("user_role") as "customer" | "chef" | "courier" | null;
            setView(role || "customer");
          }}
          userData={userData}
        />
      )}
      <FloatingChatbot />
    </div>
  );
};

export default Index;

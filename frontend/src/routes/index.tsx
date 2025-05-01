import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ShopPage from "../pages/ShopPage";

const AppRoutes = () => (
  <Router>
    <Routes>
      <Route path="/shop" element={<ShopPage />} />
      {/* Thêm các route khác tại đây */}
    </Routes>
  </Router>
);

export default AppRoutes;

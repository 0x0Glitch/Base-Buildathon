import React from "react";
import logo from "../../assets/image.png";

const Logo = () => (
  <div className="flex items-center gap-2">
    <div className="relative w-20 h-20">
      <img src={logo} alt="Orion" />
    </div>
  </div>
);

export default Logo;

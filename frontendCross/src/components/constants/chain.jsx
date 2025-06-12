// src/constants/chains.js
import optimism from "../../assets/optimism.svg";
import baseIcon from "../../assets/base.svg";
import ethIcon from "cryptocurrency-icons/svg/color/eth.svg";
import maticIcon from "cryptocurrency-icons/svg/color/matic.svg";

export const SUPERETH_ABI = [
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function decimals() view returns (uint8)",
  "function totalSupply() view returns (uint256)",
  "function balanceOf(address) view returns (uint256)",
  "function transfer(address to, uint256 amount) returns (bool)",
  "function deposit() payable",
  "function withdraw(uint256 amount)",
  "function crosschainMint(address to, uint256 amount)",
  "function crosschainBurn(address from, uint256 amount)",
  "event Deposited(address indexed user, uint256 amount)",
  "event Withdrawn(address indexed user, uint256 amount)",
  "event CrosschainMinted(address indexed receiver, uint256 amount)",
  "event CrosschainBurned(address indexed from, uint256 amount)",
];

export const CONTRACT_ADDRESS = "";
export const SUPPORTED_CHAINS = [
  {
    chainName: "Ethereum Sepolia",
    chainId: "0xaa36a7",
    chainIdDecimal: 11155111,
    icon: (
      <img
        src={ethIcon}
        alt="Ethereum Sepolia Icon"
        className="w-10 h-10 bg-transparent"
      />
    ),
  },
  {
    chainName: "Polygon Mumbai",
    chainId: "0x13881",
    chainIdDecimal: 80001,
    icon: (
      <img
        src={maticIcon}
        alt="Polygon Mumbai Icon"
        className="w-10 h-10 bg-transparent"
      />
    ),
  },
  {
    chainName: "Optimism Sepolia",
    chainId: "0xA8F3C",
    chainIdDecimal: 690556,
    icon: (
      <img
        src={optimism}
        alt="Optimism Icon"
        className="w-10 h-10 bg-transparent"
      />
    ),
  },
  {
    chainName: "Base Sepolia",
    chainId: "0x14913",
    chainIdDecimal: 84531,
    icon: (
      <img
        src={baseIcon}
        alt="Base Icon"
        className="w-10 h-10 bg-transparent"
      />
    ),
  },
];

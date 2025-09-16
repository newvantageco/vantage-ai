import dynamic from "next/dynamic";
const UserMenu = dynamic(() => import("@/components/auth/UserMenu"), { ssr: false });

export default UserMenu;

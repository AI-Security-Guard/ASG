import { BackgroundWrapper } from "./Background.style.js";

function Layout({ children }) {
    return <BackgroundWrapper>{children}</BackgroundWrapper>;
}

export default Layout;

import { SidebarContainer, CCTVButton, ListButton } from './Sidebar.style.js';

function Sidebar() {
    return (
        <>
            <SidebarContainer>
                <CCTVButton>📷 CCTV영상</CCTVButton>
                <ListButton>📋 기록</ListButton>
            </SidebarContainer>
        </>
    );
}

export default Sidebar;

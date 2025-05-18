import React from "react";
import { SidebarContainer, SidebarButton, SidebarFooter } from "./Sidebar.style.js";
import CameraAltIcon from "@mui/icons-material/CameraAlt";
import AssignmentIcon from "@mui/icons-material/Assignment";

function Sidebar() {
    return (
        <SidebarContainer>
            <div>
                <SidebarButton>
                    <div className="content">
                        <CameraAltIcon fontSize="small" />
                        <span>CCTV 영상</span>
                    </div>
                </SidebarButton>
                <SidebarButton>
                    <div className="content">
                        <AssignmentIcon fontSize="small" />
                        <span>기록</span>
                    </div>
                </SidebarButton>
            </div>
            <SidebarFooter>
                ⓒ 2025 AI-Security-Guard
                <br />
                All rights reserved
            </SidebarFooter>
        </SidebarContainer>
    );
}

export default Sidebar;

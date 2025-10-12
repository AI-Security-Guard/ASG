import React, { useState, useEffect } from "react";
import {
    ListContainer,
    UnconfirmedCountMessage,
    SuspectEntry,
    SuspectPoto,
    SuspectDetail,
    Date,
    DetailMessage,
    ConfirmCheckbox,
    IncidentInfo,
    SuspectContainer,
    SuspectColumn,
    Container,
    ListPagination,
} from "./ListPage.style.js";
import Header from "../../component/Header/Header.js";
import Sidebar from "../../component/Sidebar/Sidebar.js";
import { useNavigate } from "react-router-dom";

function ListPage() {
    const navigate = useNavigate();
    const [entries, setEntries] = useState([]);
    const [jobId, setJobId] = useState(() => localStorage.getItem("jobId"));

    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 8;
    const jobId1 = "1c995028-173f-4b0d-a5cb-10baa4203a40";
    const API_BASE = "http://127.0.0.1:5001";

    useEffect(() => {
        if (!jobId1) return;

        (async () => {
            const res = await fetch(`${API_BASE}/jobs/${jobId1}/clips`);
            if (!res.ok) {
                console.error("Failed to fetch clips", res.status);
                return;
            }

            const data = await res.json();
            const mapped = (data.clips || []).map((c, i) => ({
                id: c.clip_id ?? i,
                date: c.start_time ?? "",
                message: c.class_name === "assault" ? "폭행" : c.class_name ?? "",
                checked: false,
                clipPath: (c.clip_path || "").replace(/\\/g, "/"),
                thumbPath: c.thumb_url || "",
                start_bbox: c.start_bbox || c.bbox || null,
                clipUrl: c.clip_url || "",
            }));

            setEntries(mapped);
        })().catch((e) => console.error(e));
    }, [API_BASE, jobId1]);

    const handlePageChange = (event, page) => {
        setCurrentPage(page);
    };

    const sortedEntries = [...entries].sort((a, b) => a.checked - b.checked);
    const indexOfLastEntry = currentPage * itemsPerPage;
    const indexOfFirstEntry = indexOfLastEntry - itemsPerPage;
    const currentEntries = sortedEntries.slice(indexOfFirstEntry, indexOfLastEntry);
    const unconfirmedCount = entries.filter((entry) => !entry.checked).length;

    const handleClick = (entry) => {
        navigate("/Detail", { state: entry });
    };

    return (
        <>
            <ListContainer>
                <Header />
                <Sidebar />
                <Container>
                    <UnconfirmedCountMessage>
                        확인하지 않은 거동 수상자 목록이 {unconfirmedCount}개 있습니다.
                    </UnconfirmedCountMessage>

                    <SuspectContainer>
                        <SuspectColumn>
                            {currentEntries.slice(0, 4).map((entry) => (
                                <SuspectEntry key={entry.id} onClick={() => handleClick(entry)}>
                                    {/* 썸네일이 있으면 썸네일, 없으면 임시 이미지 */}
                                    <SuspectPoto
                                        as="img"
                                        src={entry.thumbPath ? `${API_BASE}${entry.thumbPath}` : "/image/poto.png"}
                                        alt="썸네일"
                                    />
                                    <SuspectDetail>
                                        <IncidentInfo>
                                            <Date>{entry.date}</Date>
                                            <DetailMessage>
                                                <span style={{ color: "red" }}>{entry.message}</span>이(가)
                                                발생했습니다.
                                            </DetailMessage>
                                        </IncidentInfo>
                                        <ConfirmCheckbox checked={entry.checked} disabled={true} />
                                    </SuspectDetail>
                                </SuspectEntry>
                            ))}
                        </SuspectColumn>

                        <SuspectColumn>
                            {currentEntries.slice(4, 8).map((entry) => (
                                <SuspectEntry key={entry.id} onClick={() => handleClick(entry)}>
                                    <SuspectPoto
                                        as="img"
                                        src={entry.thumbPath ? `${API_BASE}${entry.thumbPath}` : "/image/poto.png"}
                                        alt="썸네일"
                                    />
                                    <SuspectDetail>
                                        <IncidentInfo>
                                            <Date>{entry.date}</Date>
                                            <DetailMessage>
                                                <span style={{ color: "red" }}>{entry.message}</span>이(가)
                                                발생했습니다.
                                            </DetailMessage>
                                        </IncidentInfo>
                                        <ConfirmCheckbox checked={entry.checked} disabled={true} />
                                    </SuspectDetail>
                                </SuspectEntry>
                            ))}
                        </SuspectColumn>
                    </SuspectContainer>

                    <ListPagination
                        count={Math.ceil(sortedEntries.length / itemsPerPage)}
                        page={currentPage}
                        onChange={handlePageChange}
                    />
                </Container>
            </ListContainer>
        </>
    );
}

export default ListPage;

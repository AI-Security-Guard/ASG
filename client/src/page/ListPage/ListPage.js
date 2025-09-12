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
    const [jobId, setJobId] = useState(() => localStorage.getItem("jobId")); // ✅

    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 8;
    const jobId1 = "d57abdec-8dcb-4bd7-a282-12f1a8a8f9a7";
    const API_BASE = "http://127.0.0.1:5001";

    useEffect(() => {
        fetch(`${API_BASE}/jobs/${jobId}`)
            .then((r) => r.json())
            .then((data) => {
                console.log("jobs payload:", data);

                const clips = data?.results?.clips_info?.clips || [];
                console.log("clips:", clips);

                // ✅ Detail에서 쓸 모든 필드를 entries에 저장
                const mapped = clips.map((c, i) => ({
                    id: c.clip_id ?? i,
                    date: c.start_time,
                    message: c.class_name === "assault" ? "폭행" : c.class_name,
                    checked: false,
                    clipPath: c.clip_path ? c.clip_path.replace(/\\/g, "/") : "",
                    thumbPath: c.thumb_path,
                    start_bbox: c.start_bbox, // ✅ bbox 추가
                }));

                setEntries(mapped);
            })
            .catch((e) => console.error(e));
    }, [jobId]);

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

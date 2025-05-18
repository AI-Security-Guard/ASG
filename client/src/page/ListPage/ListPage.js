import React, { useState } from "react";
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

    const entries = [
        { date: "2025/05/07", message: "폭행", checked: true },
        { date: "2025/05/05", message: "데이트폭력", checked: true },
        { date: "2025/05/06", message: "도난", checked: false },
        { date: "2025/05/07", message: "폭행", checked: true },
        { date: "2025/05/08", message: "사고", checked: false },
        { date: "2025/05/09", message: "기물파손", checked: false },
        { date: "2025/05/10", message: "침입", checked: false },
        { date: "2025/05/11", message: "폭행", checked: true },
        { date: "2025/05/12", message: "투기", checked: true },
        { date: "2025/05/08", message: "사고", checked: false },
        { date: "2025/05/09", message: "기물파손", checked: false },
        { date: "2025/05/10", message: "침입", checked: false },
        { date: "2025/05/11", message: "폭행", checked: true },
        { date: "2025/05/12", message: "투기", checked: true },
    ];

    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 8;

    const handlePageChange = (event, page) => {
        setCurrentPage(page);
    };

    const sortedEntries = [...entries].sort((a, b) => a.checked - b.checked);
    const indexOfLastEntry = currentPage * itemsPerPage;
    const indexOfFirstEntry = indexOfLastEntry - itemsPerPage;
    const currentEntries = sortedEntries.slice(indexOfFirstEntry, indexOfLastEntry);
    const unconfirmedCount = entries.filter((entry) => !entry.checked).length;

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
                            {currentEntries.slice(0, 4).map((entry, index) => (
                                <SuspectEntry key={index} onClick={() => navigate("/Detail")}>
                                    <SuspectPoto src="/image/poto.png" alt="임시 이미지" />
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
                            {currentEntries.slice(4, 8).map((entry, index) => (
                                <SuspectEntry key={index} onClick={() => navigate("/Detail")}>
                                    <SuspectPoto src="/image/poto.png" alt="임시 이미지" />
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

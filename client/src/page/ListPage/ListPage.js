import React, { useState } from 'react';
import { Pagination } from '@mui/material';
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
} from './ListPage.style.js';
import Header from '../../component/Header/Header.js';

function ListPage() {
    const entries = [
        { date: '2025/05/05', message: '폭행', checked: true },
        { date: '2025/05/06', message: '도난', checked: false },
        { date: '2025/05/07', message: '폭행', checked: true },
        { date: '2025/05/08', message: '사고', checked: false },
        { date: '2025/05/09', message: '절도', checked: false },
        { date: '2025/05/10', message: '사기', checked: false },
        { date: '2025/05/11', message: '폭행', checked: true },
        { date: '2025/05/12', message: '사고', checked: true },
        { date: '2025/05/13', message: '폭행', checked: true },
        { date: '2025/05/14', message: '도난', checked: false },
        { date: '2025/05/15', message: '폭행', checked: false },
        { date: '2025/05/16', message: '사기', checked: false },
        { date: '2025/05/17', message: '절도', checked: true },
        { date: '2025/05/18', message: '사고', checked: true },
        { date: '2025/05/19', message: '폭행', checked: true },
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
            <Header />
            <ListContainer>
                <UnconfirmedCountMessage>
                    "관리자님 확인하지 않은 거동 수상자 목록이 {unconfirmedCount}개 있습니다."
                </UnconfirmedCountMessage>
                <SuspectContainer>
                    <SuspectColumn>
                        {currentEntries.slice(0, 4).map((entry, index) => (
                            <SuspectEntry key={index}>
                                <SuspectPoto src='/image/poto.png' alt='임시 이미지' />
                                <SuspectDetail>
                                    <IncidentInfo>
                                        <Date>{entry.date}</Date>
                                        <DetailMessage>
                                            <span style={{ color: 'red' }}>{entry.message}</span>이(가) 발생했습니다.
                                        </DetailMessage>
                                    </IncidentInfo>
                                    <ConfirmCheckbox checked={entry.checked} disabled={true} />
                                </SuspectDetail>
                            </SuspectEntry>
                        ))}
                    </SuspectColumn>
                    <SuspectColumn>
                        {currentEntries.slice(4, 8).map((entry, index) => (
                            <SuspectEntry key={index}>
                                <SuspectPoto src='/image/poto.png' alt='임시 이미지' />
                                <SuspectDetail>
                                    <IncidentInfo>
                                        <Date>{entry.date}</Date>
                                        <DetailMessage>
                                            <span style={{ color: 'red' }}>{entry.message}</span>이(가) 발생했습니다.
                                        </DetailMessage>
                                    </IncidentInfo>
                                    <ConfirmCheckbox checked={entry.checked} disabled={true} />
                                </SuspectDetail>
                            </SuspectEntry>
                        ))}
                    </SuspectColumn>
                </SuspectContainer>
                <Pagination
                    count={Math.ceil(sortedEntries.length / itemsPerPage)} // 정렬된 데이터를 기준으로 페이지 수 계산
                    page={currentPage}
                    onChange={handlePageChange}
                    variant='outlined'
                    shape='rounded'
                />
            </ListContainer>
        </>
    );
}

export default ListPage;

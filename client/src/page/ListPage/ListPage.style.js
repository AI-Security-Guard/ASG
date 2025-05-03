import styled, { keyframes } from 'styled-components';
import { Checkbox, Pagination } from '@mui/material';

export const ListContainer = styled.div`
    display: flex;
    flex-direction: column;
    width: 84%;
    height: 90%;
    position: absolute;
    bottom: 0;
    right: 0;
    align-items: center;
    justify-content: center;
`;

export const UnconfirmedCountMessage = styled.div`
    font-size: 25px;
    font-weight: bold;
`;

export const SuspectContainer = styled.div`
    width: 100%;
    height: 75%;
    display: flex;
    flex-direction: column;
    gap: 10%;
    align-items: center;
    justify-content: center;
`;

export const SuspectColumn = styled.div`
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    width: 80%;
    justify-items: center;
`;

export const SuspectEntry = styled.div`
    display: flex;
    flex-direction: column;
    transition: transform 0.5s ease, box-shadow 0.5s ease;
    &:hover {
        transform: scale(1.05);
        box-shadow: 0px 6px 10px rgba(0, 0, 0, 0.1), 0px 10px 20px rgba(0, 0, 0, 0.15), 0px 15px 30px rgba(0, 0, 0, 0.2);
    }
    cursor: pointer;
    border-radius: 10px;
    width: 80%;
`;

export const SuspectPoto = styled.img`
    width: 100%;
    border-radius: 10px 10px 0px 0px;
    border-top: 1px solid black;
    border-left: 1px solid black;
    border-right: 1px solid black;
    height: 70%;
`;

export const SuspectDetail = styled.div`
    width: 100%;
    border-radius: 0px 0px 10px 10px;
    background: #cbcccd;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid black;
    border-left: 1px solid black;
    border-right: 1px solid black;
    height: 80%;
`;

export const IncidentInfo = styled.div`
    font-weight: 600;
    width: 100%;
    margin-left: 5%;
`;

export const Date = styled.div``;

export const DetailMessage = styled.div`
    font-size: 13px;
`;

export const ConfirmCheckbox = styled(Checkbox)``;

export const ListPagination = styled(Pagination)`
    & .MuiPaginationItem-page.Mui-selected {
        background-color: rgba(39, 39, 39, 0.5); /* 선택된 페이지 배경: 더 진한 검정색 계열 */
        color: black;
    }

    & .MuiPaginationItem-page:hover {
        background-color: rgba(39, 39, 39, 0.2); /* 호버 시 배경: 조금 더 투명한 검정색 */
        color: black;
    }

    & .MuiPaginationItem-page:active {
        background-color: rgba(39, 39, 39, 0.5); /* 클릭 시 배경: 선택보다 약간 투명도가 낮은 진한 검정색 */
        color: black;
    }
`;

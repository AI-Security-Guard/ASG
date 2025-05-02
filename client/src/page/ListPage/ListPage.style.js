import styled, { keyframes } from 'styled-components';
import { Checkbox, FormControlLabel, Button } from '@mui/material';

export const ListContainer = styled.div`
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    gap: 10%;
    width: 100%;
`;

export const UnconfirmedCountMessage = styled.div`
    font-size: 1.5rem;
    font-weight: bold;
`;

export const SuspectContainer = styled.div`
    display: flex;
    flex-direction: column;
    gap: 5rem;
    height: 50%;
    align-items: center;
    justify-content: center;
    width: 100%;
`;

export const SuspectColumn = styled.div`
    display: flex;
    gap: 4rem;
    width: 100%;
    align-items: center;
    justify-content: center;
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
`;

export const SuspectPoto = styled.img`
    border-radius: 10px 10px 0px 0px;
    width: 18rem;
    border-top: 1px solid black; // 상단 테두리 설정
    border-left: 1px solid black; // 왼쪽 테두리 설정
    border-right: 1px solid black; // 오른쪽 테두리 설정
`;

export const SuspectDetail = styled.div`
    border-radius: 0px 0px 10px 10px;
    background: #cbcccd;
    width: 18rem;
    height: 5rem;
    display: flex;
    align-items: center;
    justify-content: space-around;
    border-bottom: 1px solid black; // 상단 테두리 설정
    border-left: 1px solid black; // 왼쪽 테두리 설정
    border-right: 1px solid black; // 오른쪽 테두리 설정
`;

export const IncidentInfo = styled.div`
    font-weight: 600;
`;

export const Date = styled.div``;

export const DetailMessage = styled.div``;

export const ConfirmCheckbox = styled(Checkbox)`
    &.Mui-checked {
        color: #000000 !important;
        opacity: 0.26 !important;
    }
`;

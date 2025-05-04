import styled from 'styled-components';

export const DetailContainer = styled.div`
    display: flex;
    flex-direction: column;
    width: 100%;
    align-items: center;
    height: 80%;
    position: absolute;
    bottom: 0;
    gap: 5%;
`;

export const Detail = styled.div`
    background-color: #b3b3b3;
    border-radius: 10px;
    width: 70%;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 3%;
    height: 100%;
    justify-content: space-around;
`;

export const TempVideo = styled.video`
    width: 90%;
    padding: 2%;
    border: 1px solid black;
    border-radius: 10px;
    background-color: black;
    height: 65%;
`;

export const DetailContent = styled.div`
    background-color: #d9d9d9;
    border: 1px solid black;
    border-radius: 10px;
    width: 90%;
    height: 15%;
    font-weight: bold;
    font-size: 1.2rem;
    padding: 2%;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
`;

export const Date = styled.div``;

export const Type = styled.div``;

export const Location = styled.div``;

export const ButtonContainer = styled.div`
    display: flex;
    justify-content: flex-end;
    width: 75%;
`;

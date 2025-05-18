import styled from "styled-components";

export const DetailContainer = styled.div`
    display: flex;
    flex-direction: column;
    width: 100%;
    min-height: 100vh;
    justify-content: center;
`;

export const Container = styled.div`
    display: flex;
    flex-direction: column;
    justify-content: center;
    width: 100%;
    align-items: center;
    margin-top: 10%;
    margin-bottom: 10%;
    gap: 10%;
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
    gap: 3%;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1), 0px 8px 16px rgba(0, 0, 0, 0.1);
`;

export const TempVideo = styled.video`
    width: 90%;
    padding: 2%;
    border: 1px solid black;
    border-radius: 10px;
    background-color: black;
    height: 70%;
`;

export const DetailContent = styled.div`
    background-color: #d9d9d9;
    border: 1px solid black;
    border-radius: 10px;
    width: 90%;
    font-weight: bold;
    font-size: 1.2rem;
    padding: 2%;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    word-break: keep-all;
    min-height: 100px;
    height: auto;
    margin-top: 3%;
`;

export const Date = styled.div``;

export const Type = styled.div``;

export const Location = styled.div``;

export const ButtonContainer = styled.div`
    display: flex;
    justify-content: flex-end;
    width: 75%;
    margin-top: 3%;
`;

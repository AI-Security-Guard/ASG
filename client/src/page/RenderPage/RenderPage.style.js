import styled from "styled-components";

export const MainLayout = styled.div`
    display: flex;
    height: 100vh;
    width: 100%;
`;

export const ContentArea = styled.div`
    position: absolute;
    bottom: 0;
    right: 0;
    width: 90%;
    height: 90%;
    display: flex;
    justify-content: center;
    align-items: center;
`;

export const PlusIcon = styled.img`
    cursor: pointer;
`;

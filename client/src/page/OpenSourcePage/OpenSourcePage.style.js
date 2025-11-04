import styled from "styled-components";

export const OpenSourceContainer = styled.div`
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 100vh;
    padding: 10%;
    background: rgba(255, 255, 255, 0.1);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.5);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
`;

export const Title = styled.div`
    font-size: 1.6rem;
    font-weight: 600;
    color: #2f3b52; /* 완전한 블랙 대신 약간 묵직한 네이비톤 */
    margin-bottom: 20px;
    text-align: left;
    letter-spacing: 0.3px;

    display: flex;
    width: 85%;
    justify-content: start;
    /* 은은한 밑줄 */
    border-bottom: 1.5px solid rgba(0, 0, 0, 0.08);
    padding-bottom: 6px;

    /* 부드러운 등장 애니메이션 (거의 티 안 나게) */
    animation: subtleFade 0.6s ease;
    @keyframes subtleFade {
        from {
            opacity: 0;
            transform: translateY(2px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;

export const OpenSourceContent = styled.div`
    width: 80%;
    max-width: 900px;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    padding: 40px;
    margin-top: 80px;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    h2 {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 10px;
        color: #222;
    }

    p {
        font-size: 1rem;
        color: #555;
        margin-bottom: 30px;
    }
`;

export const Section = styled.div`
    display: flex;
    flex-direction: column;
    gap: 20px;
`;

export const SourceList = styled.div`
    display: flex;
    flex-direction: column;
    gap: 5px;
`;

export const SourceItem = styled.div`
    border-left: 4px solid #1976d2;
    background-color: #f5f8ff;
    padding: 16px 20px;
    border-radius: 8px;

    h3 {
        margin: 0;
        font-size: 1.2rem;
        color: #1976d2;
    }

    a {
        color: #1976d2;
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }

    p {
        margin-top: 8px;
        color: #333;
        font-size: 0.95rem;
    }
`;

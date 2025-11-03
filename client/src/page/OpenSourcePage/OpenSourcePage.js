// src/pages/OpenSourcePage/OpenSourcePage.js
import React from "react";
import Header from "../../component/Header/Header.js";
import ShortButton from "../../component/ShortButton/ShortButton.js";
import {
    OpenSourceContainer,
    Title,
    OpenSourceContent,
    Section,
    SourceList,
    SourceItem,
} from "./OpenSourcePage.style.js";
import { useNavigate } from "react-router-dom";

function OpenSourcePage() {
    const navigate = useNavigate();

    const sources = [
        {
            name: "React",
            desc: "UI 구축을 위한 프론트엔드 라이브러리로, 컴포넌트 기반 아키텍처를 사용하여 재사용성과 유지보수성을 높였습니다.",
            link: "https://react.dev/",
        },
        {
            name: "Flask",
            desc: "Python 기반의 경량 웹 프레임워크로, RESTful API 서버 구현에 사용됐습니다.",
            link: "https://flask.palletsprojects.com/",
        },
        {
            name: "PyTorch",
            desc: "딥러닝 모델 학습 및 추론을 위한 프레임워크로, 영상 분석 AI 모델 구현에 활용됐습니다.",
            link: "https://pytorch.org/",
        },
        {
            name: "OpenCV",
            desc: "컴퓨터 비전 및 이미지 처리 라이브러리로, 영상 프레임 전처리 및 후처리에 사용됐습니다.",
            link: "https://opencv.org/",
        },
        {
            name: "SQLite",
            desc: "경량 데이터베이스로, 분석 결과(job, clip, thumbnail 등)을 저장 및 관리하는 데 사용됐습니다.",
            link: "https://www.sqlite.org/",
        },
        {
            name: "Axios",
            desc: "비동기 HTTP 통신을 위한 라이브러리로, React와 Flask 간 데이터 송수신을 처리했습니다.",
            link: "https://axios-http.com/",
        },
        {
            name: "styled-components",
            desc: "CSS-in-JS 스타일링 도구로, 컴포넌트 단위 스타일링을 효율적으로 관리헀습니다.",
            link: "https://styled-components.com/",
        },
        {
            name: "MUI",
            desc: "React UI 프레임워크로, 버튼, 모달 등 기본적인 UI 요소에 사용했습니다.",
            link: "https://mui.com/",
        },
    ];

    const handleBack = () => navigate(-1);

    return (
        <OpenSourceContainer>
            <Header />
            <OpenSourceContent>
                <Title>사용된 오픈소스 목록</Title>
                <Section>
                    <SourceList>
                        {sources.map((src) => (
                            <SourceItem key={src.name}>
                                <Title>
                                    <a href={src.link} target="_blank" rel="noreferrer">
                                        {src.name}
                                    </a>
                                </Title>
                                <p>{src.desc}</p>
                            </SourceItem>
                        ))}
                    </SourceList>
                </Section>
            </OpenSourceContent>
            <ShortButton txt="뒤로가기" onClick={handleBack} />
        </OpenSourceContainer>
    );
}

export default OpenSourcePage;

import React from "react";
import {
    FooterContainer,
    GitHubDiv,
    GitHubLogo,
    GitHubLetter,
    FooterInfo,
    ServiceStart,
    OpenSource,
    Developer,
} from "./Footer.style.js";

function Footer() {
    return (
        <FooterContainer>
            <GitHubDiv>
                <GitHubLogo src="/image/github.png" alt="로고 이미지" />
                <GitHubLetter
                    as="a"
                    href="https://github.com/AI-Security-Guard/AI-Security-Guard"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    GitHub Repository
                </GitHubLetter>
            </GitHubDiv>
            <ServiceStart>ⓒ 2025 AI-Security-Guard All rights reserved</ServiceStart>
            <FooterInfo>
                <OpenSource>오픈소스 라이선스</OpenSource>|<Developer>개발자 소개</Developer>
            </FooterInfo>
        </FooterContainer>
    );
}

export default Footer;

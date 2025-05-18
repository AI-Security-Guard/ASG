import React from "react";
import Header from "../../component/Header/Header.js";
import { DeveloperContainer, SlideBox, Tag } from "./DeveloperPage.style.js";
import { Swiper, SwiperSlide } from "swiper/react";
import "swiper/css";
import "swiper/css/pagination";
import { Pagination } from "swiper/modules";
import Sidebar from "../../component/Sidebar/Sidebar.js";

function DeveloperPage() {
    const slideItems = [
        {
            title: "개발자",
            members: [
                { name: "변무혁", tags: ["AI"], intro: "소개" },
                {
                    name: "박소정",
                    tags: ["frontend", "backend"],
                    intro: "안녕히 계세요~ 전 이 대학교의 모든 굴레와 속박을 벗어던지고 제 행복을 찾아 떠납니다.",
                },
                { name: "남동현", tags: ["frontend"], intro: "소개" },
                { name: "전한나", tags: ["AI", "배포"], intro: "소개" },
                { name: "김효지", tags: ["AI"], intro: "소개" },
            ],
        },
        {
            title: "개발 목표",
            content: `AI방범대 사이트는 영상을 분석하여\n거동 수상자를 감지하는 서비스를 제공합니다.`,
        },
    ];

    return (
        <>
            <Header />
            <DeveloperContainer>
                <Swiper modules={[Pagination]} pagination={{ clickable: true }} spaceBetween={30} slidesPerView={1}>
                    {slideItems.map((item, index) => (
                        <SwiperSlide key={index}>
                            <SlideBox>
                                <h2>{item.title}</h2>
                                {"members" in item ? (
                                    <ul>
                                        {item.members.map((member, i) => (
                                            <li key={i} style={{ marginBottom: "1rem" }}>
                                                <strong>{member.name}</strong>{" "}
                                                {member.tags.map((tag, j) => (
                                                    <Tag key={j}>{tag}</Tag>
                                                ))}
                                                <p style={{ marginTop: "0.3rem" }}>{member.intro}</p>
                                            </li>
                                        ))}
                                    </ul>
                                ) : (
                                    <p style={{ whiteSpace: "pre-line" }}>{item.content}</p>
                                )}
                            </SlideBox>
                        </SwiperSlide>
                    ))}
                </Swiper>
            </DeveloperContainer>
        </>
    );
}

export default DeveloperPage;

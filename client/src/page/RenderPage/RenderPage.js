import React, { useRef, useState } from "react";
import * as S from "./RenderPage.style";
import Header from "../../component/Header/Header";
import Sidebar from "../../component/Sidebar/Sidebar";
import ShortButton from "../../component/ShortButton/ShortButton";
import CustomModal from "../../component/CustomModal/CustomModal.js";
import { useNavigate } from "react-router-dom";
import { Spinner } from "../../component/CustomModal/CustomModal.style";

function RenderPage() {
    const fileInputRef = useRef(null);
    const [videoSrc, setVideoSrc] = useState(null);
    const [modalOpen, setModalOpen] = useState(false);
    const [modalState, setModalState] = useState("idle");

    const navigate = useNavigate();

    const handleIconClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            const videoURL = URL.createObjectURL(file);
            setVideoSrc(videoURL);
        }
    };

    const handleDeleteVideo = () => {
        setVideoSrc(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = null;
        }
    };

    const handleGoAnalysis = () => {
        setModalOpen(true);
        setModalState("loading");

        setTimeout(() => {
            setModalState("done");
        }, 3000); // 예시로 3초 후 완료로 변경
    };
    return (
        <>
            <S.MainLayout>
                <Header />
                <Sidebar />
                <S.ContentArea>
                    {!videoSrc && <S.PlusIcon src="/image/addToVideo.png" alt="영상 추가" onClick={handleIconClick} />}
                    {videoSrc && (
                        <>
                            <S.VideoPlayer controls>
                                <source src={videoSrc} type="video/mp4" />
                                브라우저가 video 태그를 지원하지 않습니다.
                            </S.VideoPlayer>
                            <S.ButtonWrapper>
                                <ShortButton txt="분석하기" onClick={handleGoAnalysis} />
                            </S.ButtonWrapper>
                            <S.DeleteWrapper>
                                <S.DeleteVideo
                                    src="/image/deleteVideo.png"
                                    alt="영상 삭제"
                                    onClick={handleDeleteVideo}
                                />
                            </S.DeleteWrapper>
                        </>
                    )}
                    <input
                        type="file"
                        accept="video/*"
                        style={{ display: "none" }}
                        ref={fileInputRef}
                        onChange={handleFileChange}
                    />
                </S.ContentArea>
            </S.MainLayout>
            <CustomModal
                open={modalOpen}
                onClose={() => {
                    setModalOpen(false);
                    setModalState("idle");
                }}
                title={modalState === "loading" ? "분석 중입니다" : "분석 완료"}
                message={modalState === "loading" ? "잠시만 기다려 주세요..." : "분석이 완료되었습니다."}
                icon={modalState === "loading" ? <Spinner /> : <img src="/image/logo.png" alt="로고" width={60} />}
                buttons={
                    modalState === "loading"
                        ? [] // 로딩 중엔 버튼 없음
                        : [
                              {
                                  label: "기록 보기",
                                  onClick: () => {
                                      // 기록 보기 로직
                                      setModalOpen(false);
                                      setModalState("idle");
                                  },
                              },
                              {
                                  label: "닫기",
                                  onClick: () => {
                                      setModalOpen(false);
                                      setModalState("idle");
                                  },
                              },
                          ]
                }
            />
        </>
    );
}

export default RenderPage;

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
                onClose={() => setModalOpen(false)}
                title="분석 중입니다"
                message="잠시만 기다려 주세요."
                icon={<Spinner />}
                buttons={[{ label: "취소", onClick: () => setModalOpen(false) }]}
            />
        </>
    );
}

export default RenderPage;

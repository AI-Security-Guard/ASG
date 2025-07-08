import React, { useRef, useState, useEffect } from "react";
import * as S from "./RenderPage.style";
import Header from "../../component/Header/Header";
import Sidebar from "../../component/Sidebar/Sidebar";
import ShortButton from "../../component/ShortButton/ShortButton";
import CustomModal from "../../component/CustomModal/CustomModal.js";
import { useNavigate } from "react-router-dom";
import * as D from "../../component/CustomModal/CustomModal.style";
import WarningAmberRoundedIcon from "@mui/icons-material/WarningAmberRounded";
import axios from "axios";

function RenderPage() {
    const fileInputRef = useRef(null);
    const [videoSrc, setVideoSrc] = useState(null);
    const [modalOpen, setModalOpen] = useState(false);
    const [modalState, setModalState] = useState("idle");
    const [modalType, setModalType] = useState("none");

    const navigate = useNavigate();

    useEffect(() => {
        const user = JSON.parse(localStorage.getItem("user"));
        const username = user?.username;

        const fetchSavedVideo = async () => {
            try {
                const response = await axios.get("http://127.0.0.1:5000/bringVideo", {
                    params: { username },
                    responseType: "blob", // 🎯 파일로 받아야 함!
                });

                const blob = new Blob([response.data], { type: "video/mp4" });
                const videoURL = URL.createObjectURL(blob);
                setVideoSrc(videoURL);

                console.log("가져오기 성공:", videoURL);
            } catch (err) {
                console.error("가져오기 실패:", err);
                console.log("username:", username);
            }
        };

        fetchSavedVideo();
    }, []);

    const handleIconClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (file) {
            const videoURL = URL.createObjectURL(file);
            setVideoSrc(videoURL);

            const user = JSON.parse(localStorage.getItem("user"));
            const username = user?.username;
            const formData = new FormData();
            formData.append("username", username);
            formData.append("video", file);

            try {
                const response = await axios.post("http://127.0.0.1:5000/uploadVideo", formData);
                console.log("업로드 성공:", response.data);
            } catch (err) {
                console.error("업로드 실패:", err);
            }
        }
    };

    const handleDeleteVideo = () => {
        setVideoSrc(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = null;
        }
    };

    const handleDeleteVideoClick = () => {
        setModalType("deleteConfirm");
        setModalOpen(true);
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
                                    onClick={handleDeleteVideoClick}
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
                    setModalType("none");
                }}
                title={
                    modalType === "deleteConfirm"
                        ? "삭제 하시겠습니까?"
                        : modalState === "loading"
                        ? "분석 중입니다"
                        : "분석 완료"
                }
                message={
                    modalType === "deleteConfirm"
                        ? "삭제하려면 확인 버튼을 클릭 해주세요."
                        : modalState === "loading"
                        ? "잠시만 기다려 주세요..."
                        : "분석이 완료되었습니다."
                }
                icon={
                    modalType === "deleteConfirm" ? (
                        <WarningAmberRoundedIcon style={{ fontSize: 60, color: "#6E6E6E" }} />
                    ) : (
                        <D.SpinnerWrapper>
                            <D.Spinner visible={modalState === "loading"} />
                            <D.CheckIcon visible={modalState === "done"} />
                        </D.SpinnerWrapper>
                    )
                }
                buttons={
                    modalType === "deleteConfirm"
                        ? [
                              {
                                  label: "취소",
                                  onClick: () => {
                                      setModalOpen(false);
                                      setModalType("none");
                                  },
                              },
                              {
                                  label: "확인",
                                  onClick: () => {
                                      handleDeleteVideo();
                                      setModalOpen(false);
                                      setModalType("none");
                                  },
                              },
                          ]
                        : modalState === "loading"
                        ? [
                              {
                                  label: "취소",
                                  onClick: () => {
                                      setModalOpen(false);
                                      setModalState("idle");
                                  },
                              },
                          ]
                        : [
                              {
                                  label: "기록 보기",
                                  onClick: () => {
                                      setModalOpen(false);
                                      setModalState("idle");
                                      navigate("/List");
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

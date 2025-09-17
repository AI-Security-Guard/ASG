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

function ProgressCircle({
    value,
    size = 120,
    strokeWidth = 12,
    trackColor = "#E5E7EB",
    progressColor = "#3B82F6",
    textColor = "#111827",
}) {
    const pct = Math.max(0, Math.min(100, value ?? 0));
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const dashOffset = circumference * (1 - pct / 100);

    return (
        <div style={{ position: "relative", width: size, height: size }}>
            <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke={trackColor}
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                />
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke={progressColor}
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={dashOffset}
                    style={{ transition: "stroke-dashoffset 0.3s ease" }}
                />
            </svg>
            <div
                style={{
                    position: "absolute",
                    inset: 0,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontWeight: 700,
                    fontSize: 18,
                    color: textColor,
                }}
            >
                {Math.round(pct)}%
            </div>
        </div>
    );
}

function RenderPage() {
    const fileInputRef = useRef(null);
    const [videoSrc, setVideoSrc] = useState(null);
    const [modalOpen, setModalOpen] = useState(false);
    const [modalState, setModalState] = useState("idle");
    const [modalType, setModalType] = useState("none");
    const [videoPath, setVideoPath] = useState(null);
    const [progress, setProgress] = useState(0);
    const [jobId, setJobId] = useState(null);
    const intervalRef = useRef(null);

    const stopPolling = () => {
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
        }
    };

    const navigate = useNavigate();

    useEffect(() => {
        const user = JSON.parse(localStorage.getItem("user"));
        const username = user?.username;

        const fetchSavedVideo = async () => {
            const token = localStorage.getItem("access_token");
            try {
                const response = await axios.get("http://127.0.0.1:5000/bringVideo", {
                    params: { username },
                    responseType: "blob",
                    headers: { Authorization: `Bearer ${token}` },
                });

                const contentType = response.headers["content-type"];
                if (contentType && contentType.includes("application/json")) {
                    const text = await response.data.text();
                    const json = JSON.parse(text);
                    if (json.hasVideo === false) {
                        return;
                    }
                } else {
                    const blob = new Blob([response.data], { type: "video/mp4" });
                    const videoURL = URL.createObjectURL(blob);
                    setVideoSrc(videoURL);
                }
            } catch (err) {
                console.error(err);
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

            const formData = new FormData();
            formData.append("video", file);
            const token = localStorage.getItem("access_token");
            try {
                const response = await axios.post("http://127.0.0.1:5000/uploadVideo", formData, {
                    headers: { Authorization: `Bearer ${token}` },
                });
                console.log("업로드 성공:", response.data);
                setVideoPath(response.data.user.full_path);
            } catch (err) {
                console.error("업로드 실패:", err.response?.data || err.message);
            }
        }
    };

    const handleDeleteVideo = async () => {
        const user = JSON.parse(localStorage.getItem("user"));
        const username = user?.username;

        if (!username) {
            console.error("❌ username 없음");
            return;
        }
        const token = localStorage.getItem("access_token");
        try {
            await axios.delete("http://127.0.0.1:5000/deleteVideo", {
                data: { username },
                headers: { Authorization: `Bearer ${token}` },
            });
            console.log("✅ 영상 삭제 성공");
        } catch (err) {
            console.error("❌ 영상 삭제 실패:", err.response?.data || err.message);
        }

        // 프론트 상태 초기화
        setVideoSrc(null);
        setVideoPath(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = null;
        }
    };

    const handleGoAnalysis = async () => {
        if (!videoPath) {
            console.error("❌ 서버 저장 경로(videoPath)가 없습니다.");
            return;
        }

        // 모달 열고 로딩 상태 세팅
        setModalOpen(true);
        setModalType("none");
        setModalState("loading");
        setProgress(0);

        // 혹시 살아있는 폴링이 있으면 정리
        stopPolling();

        try {
            // 1) 분석 요청
            const res = await axios.post(
                "http://127.0.0.1:5001/analyze",
                { video_path: videoPath },
                { headers: { "Content-Type": "application/json" } }
            );

            const newJobId = res.data?.job_id;
            if (!newJobId) {
                throw new Error("job_id가 응답에 없습니다.");
            }
            setJobId(newJobId);
            localStorage.setItem("jobId", newJobId);
            console.log(res.data);
            // 2) 진행률 폴링
            intervalRef.current = setInterval(async () => {
                try {
                    const jobRes = await axios.get(`http://127.0.0.1:5001/jobs/${newJobId}`, {
                        // 캐시 방지용 타임스탬프
                        params: { t: Date.now() },
                        headers: { "Cache-Control": "no-cache" },
                    });

                    // 백엔드가 0~1 스케일이면 100배, 이미 0~100이면 그대로
                    const raw = jobRes.data?.progress ?? 0;
                    const pct = Math.max(0, Math.min(100, raw > 1 ? raw : raw * 100));
                    setProgress(pct);

                    if (pct >= 100) {
                        stopPolling();
                        setModalState("done");
                        // 필요하면 자동 닫기 / 페이지 이동 등 추가
                        // setTimeout(() => { setModalOpen(false); navigate("/List"); }, 800);
                    }
                    console.log(jobRes.data);
                } catch (pollErr) {
                    console.error("진행률 조회 실패:", pollErr.response?.data || pollErr.message);
                    stopPolling();
                    setModalOpen(false);
                    setModalState("idle");
                }
            }, 1500); // 1.5초 간격
        } catch (err) {
            console.error("분석 요청 실패:", err.response?.data || err.message);
            setModalOpen(false);
            setModalState("idle");
        }
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
                    stopPolling();
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
                    ) : modalState === "loading" ? (
                        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
                            <ProgressCircle value={progress} size={120} strokeWidth={12} />
                            <div style={{ fontSize: 14, color: "#6B7280" }}>처리 중... {progress}%</div>
                        </div>
                    ) : (
                        <D.SpinnerWrapper>
                            <D.CheckIcon visible={true} />
                        </D.SpinnerWrapper>
                    )
                }
                buttons={
                    modalType === "deleteConfirm"
                        ? [
                              {
                                  label: "취소",
                                  onClick: () => {
                                      stopPolling();
                                      setModalOpen(false);
                                      setModalState("idle");
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
                                      stopPolling();
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

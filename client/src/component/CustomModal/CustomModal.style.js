import { styled, keyframes } from "@mui/material/styles";
import { Box, Button } from "@mui/material";

// ✨ 모달 등장 애니메이션
const fadeInModal = keyframes`
  from {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
`;

export const ModalBox = styled(Box)(({ theme }) => ({
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    width: 400,
    minHeight: 260,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "space-around",

    // ✨ Glass 효과 + 그라데이션 배경
    backdropFilter: "blur(16px)",
    WebkitBackdropFilter: "blur(16px)",
    background: "linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.18))",
    border: "1px solid rgba(255, 255, 255, 0.25)",

    // ✨ 그림자 + 입체감
    boxShadow: "0 20px 50px rgba(0, 0, 0, 0.3)",
    borderRadius: "20px",

    // ✨ 텍스트 스타일
    padding: theme.spacing(4),
    textAlign: "center",
    color: "#ffffff",
    fontFamily: "'Pretendard', sans-serif",

    // ✨ 애니메이션
    animation: `${fadeInModal} 0.3s ease-out forwards`,
}));

export const ButtonGroup = styled("div")({
    display: "flex",
    gap: "12px",
    justifyContent: "center",
    flexWrap: "wrap",
});

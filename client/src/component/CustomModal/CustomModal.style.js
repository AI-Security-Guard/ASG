import { styled, keyframes } from "@mui/material/styles";
import { Box } from "@mui/material";

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
    width: 420,
    minHeight: 280,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",

    background: "rgba(255, 255, 255, 0.5)",
    backdropFilter: "blur(18px)",
    WebkitBackdropFilter: "blur(18px)",
    border: "1px solid rgba(255, 255, 255, 0.3)",

    boxShadow: "0 16px 48px rgba(0, 0, 0, 0.15)",
    borderRadius: "20px",

    padding: "40px 30px",
    textAlign: "center",
    color: "#333333",
    fontFamily: "'Pretendard', sans-serif",

    animation: `${fadeInModal} 0.3s ease-out forwards`,

    "& h2": {
        fontSize: "1.6rem",
        fontWeight: 700,
        marginBottom: "1rem",
    },
    "& p": {
        fontSize: "1rem",
        color: "#444",
        marginBottom: "1.5rem",
    },
}));

export const ButtonGroup = styled("div")({
    display: "flex",
    gap: "12px",
    justifyContent: "center",
    flexWrap: "wrap",
});

export const CloseButton = styled("button")({
    position: "absolute",
    top: "16px",
    right: "16px",
    background: "transparent",
    border: "none",
    fontSize: "1.4rem",
    color: "#555",
    cursor: "pointer",
    transition: "color 0.2s ease",
    "&:hover": {
        color: "#000",
    },
});

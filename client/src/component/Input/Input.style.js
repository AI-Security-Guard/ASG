import { styled } from "@mui/material/styles";
import TextField from "@mui/material/TextField";

export const CustomInput = styled(TextField)(({ theme }) => ({
    width: "100%",
    borderRadius: "12px",
    backgroundColor: "rgba(255, 255, 255, 0.4)",
    backdropFilter: "blur(8px)",
    boxShadow: "0 2px 8px rgba(0, 0, 0, 0.08)",
    transition: "all 0.2s ease-in-out",
    "& .MuiOutlinedInput-root": {
        borderRadius: "12px",
        "& fieldset": {
            borderColor: "rgba(200, 200, 200, 0.4)",
        },
        "&:hover fieldset": {
            borderColor: "#94a3b8",
        },
        "&.Mui-focused fieldset": {
            borderColor: "#64748b",
            borderWidth: "1.5px",
        },
    },
    "& .MuiInputBase-input": {
        padding: "14px",
        color: "#1f2937",
        fontSize: "0.95rem",
    },
}));

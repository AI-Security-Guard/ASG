import * as D from "./Detail.style.js";
import Header from "../../component/Header/Header.js";
import ShortButton from "../../component/ShortButton/ShortButton.js";
import React from "react";
import { useNavigate, useLocation } from "react-router-dom";

const API_BASE = "http://127.0.0.1:5001";

function DetailPage() {
    const navigate = useNavigate();
    const { state: entry } = useLocation();

    const toWebPath = (p) => (typeof p === "string" ? p.replace(/\\/g, "/") : p);
    const joinURL = (base, path) => `${base.replace(/\/$/, "")}/${(path || "").replace(/^\//, "")}`;

    const videoPath = entry?.clipPath ? joinURL(API_BASE, toWebPath(entry.clipPath)) : null;

    const posterPath = entry?.thumbPath ? joinURL(API_BASE, toWebPath(entry.thumbPath)) : "/image/default.png";

    const occurredAt = entry?.date ?? "알 수 없음";
    const type = entry?.message ?? "알 수 없음";
    const coordinate = entry.start_bbox ?? "-";
    const startBBox = entry?.start_bbox;

    let coordinateText = "-";
    if (startBBox && startBBox.length === 4) {
        const [x1, y1, x2, y2] = startBBox;
        coordinateText = `(${x1}, ${y1}) ~ (${x2}, ${y2})`;
    }

    const GoBackButtonClick = () => navigate(-1);
    console.log("Detail entry:", entry);
    console.log("videoPath:", videoPath);
    console.log("posterPath:", posterPath);

    return (
        <>
            <D.DetailContainer>
                <Header />
                <D.Container>
                    <D.Detail>
                        <D.TempVideo
                            controls
                            preload="metadata"
                            poster={posterPath}
                            src={videoPath} // ✅ 이걸 직접 넣어주세요
                        >
                            해당 브라우저는 동영상을 지원하지 않습니다.
                        </D.TempVideo>

                        <D.DetailContent>
                            <D.Date>발생시기: {occurredAt}</D.Date>
                            <D.Type>수상행동 유형: {type}</D.Type>
                            <D.Location>최초 발생 위치: {coordinateText}</D.Location>
                        </D.DetailContent>
                    </D.Detail>

                    <D.ButtonContainer>
                        <ShortButton txt="뒤로가기" onClick={GoBackButtonClick} />
                    </D.ButtonContainer>
                </D.Container>
            </D.DetailContainer>
        </>
    );
}

export default DetailPage;

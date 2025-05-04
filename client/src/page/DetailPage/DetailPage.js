import * as D from './Detail.style.js';
import Header from '../../component/Header/Header.js';
import ShortButton from '../../component/ShortButton/ShortButton.js';
import React, { useState } from 'react';

function DetailPage() {
    const [video, setVideo] = useState('/video.mp4');
    const [date, setDate] = useState('2025/04/28/23:00:00');
    const [type, setType] = useState('살인');
    const [coordinate, setCoordinate] = useState('(123,123231)');

    return (
        <>
            <Header />
            <D.DetailContainer>
                <D.Detail>
                    <D.TempVideo controls>
                        <source src={video} type='video/mp4' />
                    </D.TempVideo>
                    <D.DetailContent>
                        <D.Date>발생시기: {date}</D.Date>
                        <D.Type>수상행동 유형: {type}</D.Type>
                        <D.Location>최초 발생 위치: {coordinate}</D.Location>
                    </D.DetailContent>
                </D.Detail>
                <D.ButtonContainer>
                    <ShortButton txt='뒤로가기' />
                </D.ButtonContainer>
            </D.DetailContainer>
        </>
    );
}

export default DetailPage;

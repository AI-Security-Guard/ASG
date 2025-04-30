import { styled } from '@mui/material/styles';
import Button from '@mui/material/Button';

export const CustomButton = styled(Button)(() => ({
    backgroundColor: '#272727',
    color: 'white',
    borderRadius: '20px',
    width: '5.5em',
    height: '2.5em',
    fontSize: '30px',
    boxShadow: 'none',
    '&:hover': {
        backgroundColor: '#a8a9aa',
        color: 'black',
        boxShadow: 'none',
    },
    '&:active': {
        backgroundColor: '#272727',
    },
}));

import { Box, Button, TextField, Typography } from "@mui/material"
import { createEmptySessionData, SessionData } from "../SessionData"
import { useEffect, useState } from "react";
import { ENDPOINT } from "../Config";
import axios from "axios";

const styles = {
    container: {
        padding: '8px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyItems: 'center',
    },
    button: {
        width: '200px',
        marginTop: '8px'
    }
}

type Props = {
    sessionData: SessionData,
    setSessionData: (sessionData: SessionData) => void,
}

enum ConnectionState {
    LOADING = 'loading',
    ERROR = 'error',
    CONNECTED = 'connected',
    DISCONNECTED = 'disconnected',
}

export default function QLToolHome(props: Props) {
    const [customId, setCustomId] = useState<string>('');
    const [joinCode, setJoinCode] = useState<string>('');
    const [connectionState, setConnectionState] = useState<ConnectionState>(props.sessionData.connected ? ConnectionState.CONNECTED : ConnectionState.DISCONNECTED);

    const createSession = () => {
        setConnectionState(ConnectionState.LOADING);
        axios.get(ENDPOINT + '/session/create')
            .catch(e => {
                console.log('Error creating session.')
                setConnectionState(ConnectionState.ERROR);
            })
            .then(res => {
                if (res == null) {
                    console.log('Error bad result data.')
                    setConnectionState(ConnectionState.ERROR);
                    return;
                }
                const json = res.data
                const sessionData = createEmptySessionData();
                if (json?.id != null) {
                    sessionData.session_id = json.id;
                }
                if (json?.connected != null) {
                    sessionData.connected = json.connected;
                }
                if (json?.join_code != null) {
                    sessionData.join_code = json.join_code;
                }
                sessionData.user_id = customId;
                props.setSessionData(sessionData);
                setConnectionState(sessionData.connected ? ConnectionState.CONNECTED : ConnectionState.DISCONNECTED);
            })
    }


    const joinSession = () => {
        axios.get(ENDPOINT + '/session/' + joinCode)
            .catch(e => {
                console.log('Error creating session. ' + e)
                setConnectionState(ConnectionState.ERROR);
            })
            .then(res => {
                if (res == null) {
                    console.log('Error bad result data.')
                    setConnectionState(ConnectionState.ERROR);
                    return;
                }
                const json = res.data
                const sessionData = createEmptySessionData();
                if (json?.id != null) {
                    sessionData.session_id = json.id;
                }
                if (json?.connected != null) {
                    sessionData.connected = json.connected;
                }
                if (json?.join_code != null) {
                    sessionData.join_code = json.join_code;
                }
                sessionData.user_id = customId;
                props.setSessionData(sessionData);
                setConnectionState(sessionData.connected ? ConnectionState.CONNECTED : ConnectionState.DISCONNECTED);
            })
    }

    const disconnectSession = () => {
        props.setSessionData(createEmptySessionData());
        setConnectionState(ConnectionState.DISCONNECTED);
    }

    const getConnectionMessage = () => {
        switch (connectionState) {
            case ConnectionState.CONNECTED: {
                return 'CONNECTED';
            }
            case ConnectionState.DISCONNECTED: {
                return 'DISCONNECTED';
            }
            case ConnectionState.LOADING: {
                return 'Loading...';
            }
            case ConnectionState.ERROR: {
                return 'ERROR';
            }
        }
    }

    return (
        <Box sx={styles.container}>
            <Typography variant='h3'>Welcome to TFT-QL</Typography>
            <Typography>Status: {getConnectionMessage()}</Typography>
            {connectionState == ConnectionState.CONNECTED && <Typography>Join Code: {props.sessionData.join_code}</Typography>}
            {connectionState == ConnectionState.CONNECTED && <Typography>ID: {props.sessionData.user_id}</Typography>}
            {connectionState == ConnectionState.CONNECTED && <Typography>SESSION ID: {props.sessionData.session_id}</Typography>}
            {connectionState == ConnectionState.CONNECTED && <Button variant="contained" color="error" sx={styles.button} onClick={disconnectSession}>Disconnect</Button>}
            {connectionState != ConnectionState.CONNECTED && <TextField sx={styles.button}  label="Custom ID" variant="outlined" value={customId} onChange={(e) => setCustomId(e.target.value)} />}
            {connectionState != ConnectionState.CONNECTED &&<TextField sx={styles.button} label="Join Code" variant="outlined" value={joinCode} onChange={(e) => setJoinCode(e.target.value)} />}
            {connectionState != ConnectionState.CONNECTED && <Button variant="contained" sx={styles.button} onClick={createSession} disabled={customId == ''}>Create Session</Button>}
            {connectionState != ConnectionState.CONNECTED && <Button variant="contained" sx={styles.button} onClick={joinSession} disabled={customId == ''}>Join Session</Button>}
        </Box>
    )
}
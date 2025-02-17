import { Card, Typography } from "@mui/material";
import { SessionData } from "./SessionData";
import { useEffect, useState } from "react";
import axios from "axios";
import { ENDPOINT } from "./Config";

const styles = {
    eventLog: {
        width: '100%',
        midHeight: '100px',
        height: '100%',
        fontFamily: 'monospace',
        font: 'Courier'
    }
}

type Props = {
    sessionData: SessionData,
}

export default function QLToolStreamer(props: Props) {
    const [eventLog, setEventLog] = useState<string>('');
    const [lastTs, setLastTs] = useState<number>(0);
    const [lastSession, setLastSession] = useState<string | null>(null);

    useEffect(() => {
        if (props.sessionData.connected && lastSession == null) {
            setEventLog(eventLog + '\nConnecting to session ' + props.sessionData.joinCode + " as " + props.sessionData.id);
            setLastSession(props.sessionData.joinCode);
        } else if (!props.sessionData.connected && lastSession != null) {
            setEventLog(eventLog + '\nDisconnected from session ' + lastSession);
            setLastSession(null);
        }
    }, [props.sessionData])

    useEffect(
        () => {
            const interval = setInterval(() => {
                if (!props.sessionData.connected) return;
                const params = new URLSearchParams({
                    ts: lastTs.toString(),
                });
                axios.get(ENDPOINT + '/session/' + props.sessionData.joinCode + '/events?' + params)
                    .then(res => {
                        const connected = res.data.connected
                        const events = res.data.events
                        if (connected == null || !connected || !events) return;
                        const events_array = Array.from(events).sort((a: any, b: any) => (a[0] - b[0]));
                        if (events_array.length == 0) return;
                        const ts = parseInt(events_array[events_array.length - 1] as string);
                        const event_strings = events_array.map((x: any) => '[' + x[1][1] + ']: ' + x[1][0]);
                        setEventLog(eventLog + '\n' + event_strings.join('\n'));
                        setLastTs(ts);
                    })
                    .catch(e => console.log('Error: ' + e))
            }, 1000);
            return () => clearInterval(interval);
        }, [props.sessionData, lastTs]
    )

    return (<Card sx={{ height: '100%' }}>
        <Typography>
            Events
        </Typography>
        <textarea spellCheck="false" value={eventLog} style={styles.eventLog} />
    </Card>)
}
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
            setEventLog(eventLog + '\nConnecting to session ' + props.sessionData.join_code + " as " + props.sessionData.user_id);
            setLastSession(props.sessionData.join_code);
        } else if (!props.sessionData.connected && lastSession != null) {
            setEventLog(eventLog + '\nDisconnected from session ' + lastSession);
            setLastSession(null);
        }

    }, [props.sessionData])

    useEffect(
        () => {
            const interval = setInterval(() => {
                if (!props.sessionData.connected) {
                    setEventLog('Not connected to a session.');
                    return;
                }
                const params = new URLSearchParams({
                    ts: lastTs.toString(),
                });
                axios.get(ENDPOINT + '/session/' + props.sessionData.session_id + '/events?' + params)
                    .then(res => {
                        const connected = res.data.connected
                        const events = res.data.events as Array<{
                            user_id: string, ts: number, tool: string, data: string
                        }>
                        if (connected == null || !connected || !events) return;
                        const events_array = events.sort((a: any, b: any) => (a.ts - b.ts));
                        if (events_array.length == 0) return;
                        const ts = events_array[events_array.length - 1].ts;
                        const event_strings = events_array.map((x) => '[' + x.user_id + '][' + x.tool + ']: ' + x.data);
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
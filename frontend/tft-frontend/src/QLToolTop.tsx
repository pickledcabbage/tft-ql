import { Box, Card, TextField } from "@mui/material";
import { useEffect, useState } from "react";
import { ENDPOINT } from "./Config";
import { SessionData } from "./SessionData";
import axios from "axios";

const styles = {
    searchBar: {
        width: '100%'
    },
    output: {
        width: '100%',
        midHeight: '100px',
        height: '100%',
        fontFamily: 'monospace',
        font: 'Courier'
    }
}

type Props = {
    sessionData: SessionData,
    cachedState: any,
    cacheState: (state: any) => void
}

export default function QLToolTop(props: Props) {
    const [query, setQuery] = useState('');
    const [output, setOutput] = useState('Empty.');

    useEffect(
        () => {
            if (props.cachedState?.query != null && props.cachedState.query != query) {
                setQuery(query);
            }
            if (props.cachedState?.output != null && props.cachedState.output != output) {
                setOutput(output);
            }
        },
        [props.cachedState]
    )

    const fetchData = () => {
        let params;
        if (props.sessionData.connected) {
            params = {
                session_id: props.sessionData.session_id,
                user_id: props.sessionData.user_id,
                query,
            }
        } else {
            params = {
                query,
            }
        }
        setOutput('Loading...');
        axios.get(ENDPOINT + '/test?' + new URLSearchParams(params)).catch(e => setOutput('Error: ' + e)).then(res => {
            if (res == null) {
                setOutput('Bad response.');

            } else {
                if (res.data.error != null) {
                    setOutput(res.data.error);
                } else {
                    setOutput(res.data.data);
                }
                props.cacheState({ output: res.data.data });
            }
        })
    }

    return (
        <Card sx={{ height: '100%' }}>
            <form onSubmit={(e) => { e.preventDefault(); fetchData(); }}>
                <TextField placeholder="Query" sx={styles.searchBar} variant="outlined" value={query} onChange={(e) => setQuery(e.target.value)} size="small" />
            </form>
            <textarea spellCheck="false" value={output} style={styles.output} />
        </Card>
    )
}
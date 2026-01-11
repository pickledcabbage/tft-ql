import { Autocomplete, Box, Button, Card, FormControl, InputLabel, MenuItem, Select, TextField } from "@mui/material";
import { useEffect, useState } from "react";
import { ENDPOINT } from "./Config";
import axios from "axios";

const styles = {
    form: {
        display: 'flex',
        flexDirection: 'column' as const,
        gap: '16px',
        padding: '16px'
    },
    select: {
        width: '100%'
    }
}

export default function QLToolAliasAdder() {
    const [aliasType, setAliasType] = useState<string>('');
    const [apiIds, setApiIds] = useState<string[]>([]);
    const [selectedApiId, setSelectedApiId] = useState<string>('');
    const [alias, setAlias] = useState<string>('');
    const [status, setStatus] = useState<string>('');

    useEffect(() => {
        if (aliasType) {
            axios.get(ENDPOINT + '/api_ids/' + aliasType)
                .then(res => {
                    setApiIds(res.data.api_ids || []);
                    setSelectedApiId('');
                })
                .catch(e => setStatus('Error fetching API IDs: ' + e));
        }
    }, [aliasType]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!aliasType || !selectedApiId || !alias) {
            setStatus('Please fill in all fields.');
            return;
        }

        axios.post(ENDPOINT + '/alias/add', {
            api_id: selectedApiId,
            alias: alias,
            type: aliasType
        })
            .then(res => {
                if (res.data.success) {
                    setStatus('Alias added successfully!');
                    setAlias('');
                } else {
                    setStatus('Error: ' + res.data.error);
                }
            })
            .catch(e => setStatus('Error: ' + e));
    };

    return (
        <Card sx={{ height: '100%' }}>
            <form onSubmit={handleSubmit} style={styles.form}>
                <FormControl fullWidth size="small">
                    <InputLabel>Alias Type</InputLabel>
                    <Select
                        value={aliasType}
                        label="Alias Type"
                        onChange={(e) => setAliasType(e.target.value)}
                    >
                        <MenuItem value="champ">Champion</MenuItem>
                        <MenuItem value="item">Item</MenuItem>
                        <MenuItem value="trait">Trait</MenuItem>
                    </Select>
                </FormControl>

                <Autocomplete
                    options={apiIds}
                    value={selectedApiId || null}
                    onChange={(_e, newValue) => setSelectedApiId(newValue ?? '')}
                    disabled={!aliasType}
                    size="small"
                    renderInput={(params) => <TextField {...params} label="API ID" />}
                />

                <TextField
                    placeholder="Alias"
                    variant="outlined"
                    value={alias}
                    onChange={(e) => setAlias(e.target.value)}
                    size="small"
                    fullWidth
                />

                <Button type="submit" variant="contained">Add Alias</Button>

                {status && <Box sx={{ color: status.includes('Error') ? 'red' : 'green' }}>{status}</Box>}
            </form>
        </Card>
    )
}

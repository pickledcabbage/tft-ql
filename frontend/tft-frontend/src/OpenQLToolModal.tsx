import { useState } from "react";
import { QLTool } from "./QLTool"
import { Box, Button, Card, MenuItem, Modal, Select, Typography } from "@mui/material";


const styles = {
    selector: {
        width: '100px',
        margin: '8px',
    },
    button: {
        margin: '8px',
    },
    card: {
        width: '50vw',
        height: '50vh',
        padding: '8px',
        alignItems: 'center',
    },
    modal: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
    }
}

type Props = {
    replaceTool: (tool: QLTool) => void,
    isOpen: boolean,
    setModalOpen: (state: boolean) => void,
}

export default function OpenQLToolModal(props: Props) {
    const [tool, setTool] = useState<QLTool>(QLTool.TEST)

    return (
        <Modal sx={styles.modal} open={props.isOpen} onClose={() => props.setModalOpen(false)}>
            <Card sx={styles.card}>
                <Typography variant='h5'>
                    Tool Opener
                </Typography>
                <Select value={tool} onChange={(e) => setTool(e.target.value as QLTool)} size="small" sx={styles.selector}>
                    {Object.values(QLTool).map(tool => (<MenuItem value={tool}>{tool}</MenuItem>))}
                </Select>
                <Button variant='contained' sx={styles.button} onClick={() => { props.replaceTool(tool); props.setModalOpen(false); }}>Open</Button>
            </Card>
        </Modal>
    );
}
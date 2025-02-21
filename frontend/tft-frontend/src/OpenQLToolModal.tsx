import { useState } from "react";
import { QLTool } from "./QLTool"
import { Autocomplete, Card,  Modal, TextField, } from "@mui/material";


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
    const [tool, setTool] = useState<QLTool>(QLTool.QUERY)

    return (
        <Modal sx={styles.modal} open={props.isOpen} onClose={() => props.setModalOpen(false)}>
            <Card sx={styles.card}>
                <form onSubmit={(e) => { e.preventDefault(); props.replaceTool(tool); props.setModalOpen(false); }}>
                    <Autocomplete disablePortal options={Object.values(QLTool)} onChange={(_e, newValue) => {setTool(newValue ?? QLTool.QUERY)}} sx={{width: '100%'}} renderInput={(params) => <TextField autoFocus {...params} label="Tool" />}/>
                </form>
            </Card>
        </Modal>
    );
}
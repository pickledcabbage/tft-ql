import { Box, Button, MenuItem, Select, Typography } from "@mui/material";
import { QLTool } from "./QLTool";
import { useState } from "react";

const styles = {
    selector: {
        width: '100px',
        margin: '8px',
    },
    button: {
        margin: '8px',
    }
}

type Props = {
    replaceSelf: (tool: QLTool) => void,
}

export default function QLToolOpen(props: Props) {
    const [tool, setTool] = useState<QLTool>(QLTool.TEST)

    return (
        <Box>
           <Typography variant='h5'>
            Tool Opener
            </Typography>
            <Select value={tool} onChange={(e) => setTool(e.target.value as QLTool)} sx={styles.selector}>
            {Object.values(QLTool).map(tool => (<MenuItem value={tool}>{tool}</MenuItem>))}
            </Select>
            <Button variant='contained' sx={styles.button} onClick={() => props.replaceSelf(tool)}>Open</Button>
        </Box>
    );
}
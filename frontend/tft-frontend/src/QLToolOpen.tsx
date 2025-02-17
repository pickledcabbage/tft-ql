import { Box, Button, MenuItem, Select, Typography } from "@mui/material";
import { QLTool } from "./QLTool";
import { useState } from "react";

const styles = {
    selector: {
        width: '100px'
    }
}

export default function QLToolOpen() {
    const [tool, setTool] = useState<QLTool>(QLTool.TEST)

    return (
        <Box>
           <Typography variant='h5'>
            Tool Opener
            </Typography>
            <Select value={tool} onChange={(e) => setTool(e.target.value as QLTool)} sx={styles.selector}>
            {Object.keys(QLTool).map(tool => (<MenuItem value={tool}>{tool}</MenuItem>))}
            </Select>
            <Button variant='contained'>Open</Button>
        </Box>
    );
}
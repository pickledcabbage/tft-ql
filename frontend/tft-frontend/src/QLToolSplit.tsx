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
    splitSelf: (tool: QLTool, direction: 'vertical' | 'horizontal') => void,
}

export default function QLToolOpen(props: Props) {
    const [tool, setTool] = useState<QLTool>(QLTool.TEST);
    const [direction, setDirection] = useState<'vertical' | 'horizontal'>('horizontal');

    return (
        <Box>
           <Typography variant='h5'>
            Tool Splitter
            </Typography>
            <Select value={tool} onChange={(e) => setTool(e.target.value as QLTool)} sx={styles.selector}>
            {Object.values(QLTool).map(tool => (<MenuItem value={tool}>{tool}</MenuItem>))}
            </Select>
            <Select value={direction} onChange={(e) => setDirection(e.target.value as ('vertical' | 'horizontal'))} sx={styles.selector}>
            <MenuItem value={'vertical'}>vertical</MenuItem>
            <MenuItem value={'horizontal'}>horizontal</MenuItem>
            </Select>
            <Button variant='contained' sx={styles.button} onClick={() => props.splitSelf(tool, direction)}>Split</Button>
        </Box>
    );
}
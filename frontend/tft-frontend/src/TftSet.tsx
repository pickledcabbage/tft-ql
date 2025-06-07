
export type ChampData = {
    apiName: string,
    name: string,
    traits: Array<string>,
    cost: number,
};

export type TraitData = {
    apiName: string,
    name: string,
    tiers: Array<number>,
    units: Array<string>,
};

export type ItemData = {
    apiName: string,
    name: string,
    composition: Array<string>,
}

export type TftSet = {
    set_id: string
}

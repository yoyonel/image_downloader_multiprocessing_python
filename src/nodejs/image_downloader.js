const request = require('request').defaults({
    pool: {maxSockets: Infinity},
    timeout: 10 * 1000,
});
const bluebird = require('bluebird');
const fs = require('fs-extra');
var log = require('single-line-log').stdout;
const CONCURRENCY_LEVEL = 50;

async function download(url, index) {
    log("Images retains: " + index);

    if (!url) {
        return Promise.resolve();
    }
    return new Promise((resolve, reject) => {
        const r = request(url);
        const f = fs.createWriteStream(`cats/${index}.jpg`);
        r.on('error', reject);
        r.pipe(f);
        f.on('finish', resolve);
        f.on('error', reject);
    })
        .catch((err) => {
            console.log(`Skipping error ${err.message} for ${index}`)
        })
}

async function main() {
    const catsBuffer = await fs.readFile('cats.txt');
    const cats = catsBuffer.toString().split('\n');
    await bluebird.map(cats, download, {concurrency: CONCURRENCY_LEVEL})
}

main()
    .then(() => console.log('End.'))
    .catch((err) => console.log(`Error: ${err.toString()}\n${err.stack}`))
;
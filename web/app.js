const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');
const statusDiv = document.getElementById('status');
const resultsDiv = document.getElementById('results');

function createVideoElement(video) {
    const container = document.createElement('div');
    container.className = 'video-item';

    const thumb = document.createElement('img');
    thumb.className = 'thumbnail';
    thumb.src = video.thumbnail || '';
    container.appendChild(thumb);

    const details = document.createElement('div');
    details.className = 'details';

    const title = document.createElement('a');
    title.className = 'title';
    title.href = video.url;
    title.target = '_blank';
    title.textContent = video.title;
    details.appendChild(title);

    const site = document.createElement('div');
    site.className = 'site';
    site.textContent = `Site: ${video.site} | Duration: ${video.duration} | Views: ${video.views}`;
    details.appendChild(site);

    container.appendChild(details);

    return container;
}

async function performSearch() {
    const query = searchInput.value.trim();
    if (!query) {
        statusDiv.textContent = "Please enter a search term.";
        return;
    }
    statusDiv.textContent = "Searching...";
    resultsDiv.innerHTML = '';

    try {
        const resp = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
        if (!resp.ok) throw new Error("Network response was not ok");
        const data = await resp.json();
        if (data.videos.length === 0) {
            resultsDiv.textContent = "No results found.";
        } else {
            data.videos.forEach(video => {
                resultsDiv.appendChild(createVideoElement(video));
            });
        }
        statusDiv.textContent = `Found ${data.total_results} videos from ${data.scraped_sites} sites.`;
    } catch (err) {
        statusDiv.textContent = "Error during search: " + err.message;
    }
}

searchButton.addEventListener('click', performSearch);
searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') performSearch();
});

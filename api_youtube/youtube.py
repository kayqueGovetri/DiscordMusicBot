from googleapiclient.discovery import build

from constants import API_YOUTUBE_TOKEN


class Youtube:
    def __init__(self):
        self.api = build("youtube", "v3", developerKey=API_YOUTUBE_TOKEN)
        self._search_response = None

    def get_link_by_name(self, name):
        search_response = (
            self.api.search()
            .list(q=name, type="video", part="id,snippet", maxResults=1)
            .execute()
        )

        if len(search_response) == 0:
            raise Exception("Não achamos nenhum vídeo com esse nome.")

        search_videos = []

        video_response = {}
        for search_result in search_response.get("items", []):
            search_videos.append(search_result["id"]["videoId"])
            video_ids = ",".join(search_videos)

            video_response = (
                self.api.videos()
                .list(id=video_ids, part="snippet, recordingDetails")
                .execute()
            )

        id_video = ""

        for video_result in video_response.get("items", []):
            id_video = video_result["id"]

        link_youtube = f"https://www.youtube.com/watch?v={id_video}"
        return link_youtube

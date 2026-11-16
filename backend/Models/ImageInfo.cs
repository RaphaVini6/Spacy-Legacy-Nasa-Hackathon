namespace Backend.Models;

// where an image comes from, so the site can show its source when the user clicks it
public enum ImageKind { NasaPhoto, NasaIllustration, NasaDiagram, TeamIllustration }

public class ImageSourceData
{
    public ImageKind Kind { get; set; }
    // NASA credit, or for team illustrations the NASA reference used to draw it
    public string Credit { get; set; } = "";
    public string Url { get; set; } = "";
}

public class ImageCatalog
{
    public Dictionary<string, ImageSourceData> Images { get; set; } = new();
}

public record ImageRef(string Src, ImageKind? Kind, string? Credit, string? SourceUrl);

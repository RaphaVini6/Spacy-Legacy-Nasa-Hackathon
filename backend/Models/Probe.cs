using Backend.Localization;

namespace Backend.Models;

public class ProbeData
{
    public string Id { get; set; } = "";
    public LocalizedText Name { get; set; } = new();
    public LocalizedText Equipment { get; set; } = new();
    public LocalizedText Mission { get; set; } = new();
    public Destination Destination { get; set; }
    public ProbeType Type { get; set; }
    public string Launch { get; set; } = "";
    public string Date { get; set; } = "";
    public DateKind DateKind { get; set; }
    public ProbeStatus Status { get; set; }
    public LocalizedText StatusDetail { get; set; } = new();
    public LocalizedText Location { get; set; } = new();
    public double? Latitude { get; set; }
    public double? Longitude { get; set; }
    public LocalizedText Function { get; set; } = new();
    public LocalizedText MechanicalReuse { get; set; } = new();
    public LocalizedText? KeyComponents { get; set; }
    public Source Source { get; set; } = new();
    public Reliability Reliability { get; set; }
    public LocalizedText? ReliabilityNote { get; set; }
    public string? ImageUrl { get; set; }
    public string? ImageCredit { get; set; }
    public List<string> Gallery { get; set; } = new();

    public Probe ToDto(string lang) => new(
        Id, Name.Get(lang), Equipment.Get(lang), Mission.Get(lang), Destination, Type, Launch, Date, DateKind, Status,
        StatusDetail.Get(lang), Location.Get(lang), Latitude, Longitude, Function.Get(lang), MechanicalReuse.Get(lang),
        KeyComponents?.Get(lang), Source, Reliability, ReliabilityNote?.Get(lang), ImageUrl, ImageCredit, Gallery);
}

public class Source
{
    public string Name { get; set; } = "";
    public string? Url { get; set; }
    // NSSDCA catalog id, e.g. 1969-059C
    public string? NssdcaId { get; set; }
    public string? NssdcaUrl => NssdcaId is null ? null : $"https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id={NssdcaId}";
}

public record Probe(
    string Id, string Name, string Equipment, string Mission, Destination Destination, ProbeType Type,
    string Launch, string Date, DateKind DateKind, ProbeStatus Status, string StatusDetail, string Location,
    double? Latitude, double? Longitude, string Function, string MechanicalReuse, string? KeyComponents,
    Source Source, Reliability Reliability, string? ReliabilityNote,
    string? ImageUrl, string? ImageCredit, List<string> Gallery);

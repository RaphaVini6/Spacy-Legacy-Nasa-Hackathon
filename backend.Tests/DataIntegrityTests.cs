using System.Globalization;
using System.Reflection;
using System.Text.RegularExpressions;
using Backend.Localization;
using Backend.Models;
using Xunit;

namespace Backend.Tests;

// The site content lives in JSON files and C# dictionaries; a typo there would only show up in production.
public class DataIntegrityTests
{
    private static readonly string[] Languages = Lang.Supported;

    public static IEnumerable<object[]> ProbeIds() => TestHost.Store.Probes.Select(p => new object[] { p.Id });
    public static IEnumerable<object[]> ComponentIds() => TestHost.Store.Components.Select(c => new object[] { c.Id });

    [Fact]
    public void Ids_are_unique()
    {
        Assert.Equal(TestHost.Store.Probes.Count, TestHost.Store.Probes.Select(p => p.Id.ToLowerInvariant()).Distinct().Count());
        Assert.Equal(TestHost.Store.Components.Count, TestHost.Store.Components.Select(c => c.Id.ToLowerInvariant()).Distinct().Count());
    }

    [Fact]
    public void The_collection_has_27_artifacts() =>
        Assert.Equal(27, TestHost.Store.Probes.Count);

    [Theory, MemberData(nameof(ProbeIds))]
    public void Probe_texts_exist_in_every_language(string id)
    {
        var p = TestHost.Store.Probe(id)!;
        // names and places are proper nouns ("Pioneer 10", "Oceanus Procellarum"): English is enough,
        // LocalizedText.Get falls back to it
        AssertHasEnglish(id, "Name", p.Name);
        AssertHasEnglish(id, "Mission", p.Mission);
        AssertHasEnglish(id, "Location", p.Location);

        // prose must be complete in every language
        var required = new Dictionary<string, LocalizedText>
        {
            ["Function"] = p.Function, ["MechanicalReuse"] = p.MechanicalReuse,
        };
        foreach (var (field, text) in required) AssertTranslated(id, field, text);

        // optional texts, when present, must also be complete
        var optional = new Dictionary<string, LocalizedText?>
        {
            ["FunctionDetails"] = p.FunctionDetails, ["MechanicalReuseDetails"] = p.MechanicalReuseDetails,
            ["KeyComponents"] = p.KeyComponents, ["KeyComponentsDetails"] = p.KeyComponentsDetails,
            ["RoboticsApplication"] = p.RoboticsApplication, ["RoboticsApplicationDetails"] = p.RoboticsApplicationDetails,
            ["ImageAudioDescription"] = p.ImageAudioDescription, ["CoordinatesNote"] = p.CoordinatesNote,
            ["ReliabilityNote"] = p.ReliabilityNote, ["Scenario.Summary"] = p.Scenario?.Summary,
        };
        foreach (var (field, text) in optional.Where(kv => kv.Value is not null)) AssertTranslated(id, field, text!);
    }

    // Narration prints a full date; anything else (e.g. just "2003") is read out as-is.
    // Spirit and Opportunity currently have Launch = "2003" - allowed here, but worth completing.
    [Theory, MemberData(nameof(ProbeIds))]
    public void Probe_dates_are_valid_and_in_order(string id)
    {
        var p = TestHost.Store.Probe(id)!;
        var format = new Regex(@"^\d{4}(-\d{2}-\d{2})?$");

        Assert.Matches(format, p.Launch);
        Assert.Matches(format, p.Date);
        if (p.Launch.Length == 10) Assert.True(DateOnly.TryParseExact(p.Launch, "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out _), $"{id}: Launch '{p.Launch}'");
        if (p.Date.Length == 10) Assert.True(DateOnly.TryParseExact(p.Date, "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out _), $"{id}: Date '{p.Date}'");
        Assert.True(string.CompareOrdinal(p.Date[..4], p.Launch[..4]) >= 0, $"{id}: date is before launch");
    }

    [Theory, MemberData(nameof(ProbeIds))]
    public void Probe_has_a_source_and_valid_coordinates(string id)
    {
        var p = TestHost.Store.Probe(id)!;

        Assert.False(string.IsNullOrWhiteSpace(p.Source.Name), $"{id}: source name");
        if (p.Source.Url is not null)
            Assert.True(Uri.TryCreate(p.Source.Url, UriKind.Absolute, out var uri) && uri.Scheme == Uri.UriSchemeHttps, $"{id}: source url '{p.Source.Url}'");
        Assert.Equal(p.Latitude is null, p.Longitude is null);
        if (p.Latitude is { } lat) Assert.InRange(lat, -90, 90);
        if (p.Longitude is { } lon) Assert.InRange(lon, -180, 360);
    }

    [Theory, MemberData(nameof(ProbeIds))]
    public void Probe_images_are_listed_in_the_image_catalog(string id)
    {
        var p = TestHost.Store.Probe(id)!;
        var images = new[] { p.Image }.Concat(p.GalleryImages).OfType<ImageRef>().ToList();

        foreach (var i in images)
        {
            Assert.True(i.Kind is not null, $"{id}: {i.Src} is not in images.json");
            Assert.False(string.IsNullOrWhiteSpace(i.Credit), $"{id}: {i.Src} has no credit");
            Assert.False(string.IsNullOrWhiteSpace(i.SourceUrl), $"{id}: {i.Src} has no source url");
        }
    }

    [Theory, MemberData(nameof(ProbeIds))]
    public void Probe_real_hardware_points_to_existing_parts_of_the_right_category(string id)
    {
        var p = TestHost.Store.Probe(id)!;

        foreach (var (category, componentId) in p.RealHardware)
        {
            var c = TestHost.Store.Component(componentId);
            Assert.True(c is not null, $"{id}: component '{componentId}' does not exist");
            Assert.True(c!.Category == category, $"{id}: '{componentId}' is {c.Category}, listed as {category}");
        }
        // a simulable probe needs a part in every category, otherwise the model silently skips it
        if (p.Scenario is not null)
            Assert.Equal(Enum.GetValues<HardwareCategory>().Order(), p.RealHardware.Keys.Order());
    }

    [Theory, MemberData(nameof(ProbeIds))]
    public void Probe_scenario_is_consistent(string id)
    {
        var s = TestHost.Store.Probe(id)!.Scenario;
        if (s is null) return;

        Assert.True(s.PlannedDurationDays > 0, id);
        Assert.True((s.ActualDurationDays ?? s.PlannedDurationDays) > 0, id);
        if (s.MinTempC is { } min && s.MaxTempC is { } max) Assert.True(min < max, id);
        foreach (var d in s.DustStorms)
        {
            Assert.True(d.StartDay >= 1 && d.DurationDays >= 1, $"{id}: storm days");
            Assert.InRange(d.LightFactor, 0, 1);
            AssertTranslated(id, "DustStorm.Description", d.Description);
        }
    }

    [Theory, MemberData(nameof(ComponentIds))]
    public void Component_values_are_sane(string id)
    {
        var c = TestHost.Store.Component(id)!;

        AssertHasEnglish(id, "Name", c.Name);   // part names are proper nouns ("SNAP-27 RTG")
        AssertTranslated(id, "Description", c.Description);
        Assert.True(c.MassKg >= 0 && c.OutputW >= 0 && c.ConsumptionW >= 0 && c.CapacityWh >= 0 && c.NightConsumptionW >= 0, id);
        Assert.True(c.DegradationPctPerDay >= 0, id);
        Assert.True(c.MinTempC < c.MaxTempC, $"{id}: temperature range");
        Assert.InRange(c.RadiationTolerance, 0, 10);
        if (c.ServiceLifeDays is { } days) Assert.True(days > 0, id);
        if (c.NeedsSunlight) Assert.True(c.OutputW > 0, $"{id}: needs sunlight but produces nothing");
    }

    [Fact]
    public void Every_hardware_category_has_at_least_two_options()
    {
        foreach (var cat in Enum.GetValues<HardwareCategory>())
            Assert.True(TestHost.Store.Components.Count(c => c.Category == cat) >= 2, $"category {cat} has fewer than 2 options");
    }

    // ---- server messages (Localization/Messages.cs) ----

    [Fact]
    public void Every_server_message_exists_in_every_language()
    {
        foreach (var (key, text) in AllMessages())
            AssertTranslated(key, "message", text);
    }

    [Fact]
    public void Message_placeholders_match_across_languages()
    {
        foreach (var (key, text) in AllMessages())
        {
            var reference = Placeholders(text["en"]);
            foreach (var lang in Languages)
                Assert.True(reference.SetEquals(Placeholders(text[lang])), $"{key} [{lang}]: placeholders differ from English");
        }
    }

    [Fact]
    public void Missing_message_key_returns_the_key_itself() =>
        Assert.Equal("no.such.key", Messages.Get("no.such.key", "en"));

    // ---- helpers ----

    private static void AssertHasEnglish(string owner, string field, LocalizedText text) =>
        Assert.True(text.TryGetValue("en", out var v) && !string.IsNullOrWhiteSpace(v), $"{owner}.{field} is missing 'en'");

    private static void AssertTranslated(string owner, string field, LocalizedText text)
    {
        foreach (var lang in Languages)
            Assert.True(text.TryGetValue(lang, out var v) && !string.IsNullOrWhiteSpace(v), $"{owner}.{field} is missing '{lang}'");
    }

    private static HashSet<string> Placeholders(string s) =>
        Regex.Matches(s, @"\{(\d+)").Select(m => m.Groups[1].Value).ToHashSet();

    private static Dictionary<string, LocalizedText> AllMessages() =>
        (Dictionary<string, LocalizedText>)typeof(Messages)
            .GetField("All", BindingFlags.NonPublic | BindingFlags.Static)!.GetValue(null)!;
}

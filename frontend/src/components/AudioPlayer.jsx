import { useState, useRef, useEffect } from 'react';
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX } from 'lucide-react';

function formatTime(s) {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${m}:${sec.toString().padStart(2, '0')}`;
}

export default function AudioPlayer({ src, title = 'Call Recording' }) {
  const audioRef = useRef(null);
  const canvasRef = useRef(null);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [muted, setMuted] = useState(false);
  const [volume, setVolume] = useState(0.8);
  const animFrameRef = useRef(null);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const onTimeUpdate = () => setCurrentTime(audio.currentTime);
    const onLoadedMetadata = () => setDuration(audio.duration);
    const onEnded = () => setPlaying(false);

    audio.addEventListener('timeupdate', onTimeUpdate);
    audio.addEventListener('loadedmetadata', onLoadedMetadata);
    audio.addEventListener('ended', onEnded);

    return () => {
      audio.removeEventListener('timeupdate', onTimeUpdate);
      audio.removeEventListener('loadedmetadata', onLoadedMetadata);
      audio.removeEventListener('ended', onEnded);
    };
  }, []);

  // Draw waveform
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Generate fake waveform bars
    const bars = 60;
    const barWidth = width / bars;
    const waveData = Array.from({ length: bars }, () => 0.3 + Math.random() * 0.7);

    const draw = () => {
      ctx.clearRect(0, 0, width, height);
      const progress = duration > 0 ? currentTime / duration : 0;

      waveData.forEach((val, i) => {
        const x = i * barWidth;
        const barHeight = val * height * 0.8;
        const y = (height - barHeight) / 2;
        const isPlayed = i / bars < progress;

        ctx.fillStyle = isPlayed ? '#6366f1' : 'var(--border-color)';
        ctx.fillStyle = isPlayed ? '#6366f1' : '#e2e8f0';
        ctx.beginPath();
        ctx.roundRect(x + 1, y, barWidth - 2, barHeight, 2);
        ctx.fill();
      });

      if (playing) {
        animFrameRef.current = requestAnimationFrame(draw);
      }
    };

    draw();
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [currentTime, duration, playing]);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (playing) {
      audio.pause();
    } else {
      audio.play();
    }
    setPlaying(!playing);
  };

  const toggleMute = () => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.muted = !muted;
    setMuted(!muted);
  };

  const handleVolumeChange = (e) => {
    const val = parseFloat(e.target.value);
    setVolume(val);
    if (audioRef.current) audioRef.current.volume = val;
  };

  const skip = (seconds) => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = Math.max(0, Math.min(duration, audio.currentTime + seconds));
  };

  const handleSeek = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percent = x / rect.width;
    if (audioRef.current) {
      audioRef.current.currentTime = percent * duration;
    }
  };

  return (
    <div className="rounded-xl border p-4" style={{ borderColor: 'var(--border-color)', background: 'var(--bg-tertiary)' }}>
      <audio ref={audioRef} src={src} preload="metadata" />

      <div className="flex items-center gap-3 mb-3">
        <p className="text-sm font-semibold truncate" style={{ color: 'var(--text-primary)' }}>{title}</p>
      </div>

      {/* Waveform */}
      <div
        className="cursor-pointer rounded-lg overflow-hidden mb-3"
        onClick={handleSeek}
        style={{ height: 60 }}
      >
        <canvas
          ref={canvasRef}
          width={600}
          height={60}
          className="w-full h-full"
        />
      </div>

      {/* Progress Bar */}
      <div className="relative h-1.5 rounded-full cursor-pointer mb-3" style={{ background: 'var(--border-color)' }} onClick={handleSeek}>
        <div
          className="absolute h-full rounded-full transition-all"
          style={{ width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%`, background: 'linear-gradient(90deg, #6366f1, #3b82f6)' }}
        />
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button onClick={() => skip(-10)} className="p-1.5 rounded-lg transition-colors" style={{ color: 'var(--text-secondary)' }} onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-secondary)'} onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}>
            <SkipBack size={16} />
          </button>
          <button
            onClick={togglePlay}
            className="w-10 h-10 rounded-full flex items-center justify-center text-white transition-all hover:scale-105"
            style={{ background: 'linear-gradient(135deg, #6366f1, #3b82f6)' }}
          >
            {playing ? <Pause size={18} /> : <Play size={18} className="ml-0.5" />}
          </button>
          <button onClick={() => skip(10)} className="p-1.5 rounded-lg transition-colors" style={{ color: 'var(--text-secondary)' }} onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-secondary)'} onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}>
            <SkipForward size={16} />
          </button>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs font-mono tabular-nums" style={{ color: 'var(--text-muted)' }}>
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>
          <div className="flex items-center gap-1">
            <button onClick={toggleMute} className="p-1" style={{ color: 'var(--text-muted)' }}>
              {muted ? <VolumeX size={14} /> : <Volume2 size={14} />}
            </button>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={muted ? 0 : volume}
              onChange={handleVolumeChange}
              className="w-16 h-1 accent-violet-500"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
